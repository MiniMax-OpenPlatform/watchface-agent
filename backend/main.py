"""
表盘 Code Agent Backend - FastAPI Application
生成标准 HTML/CSS/JS 表盘代码
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
import uuid
import shutil
from pathlib import Path
import zipfile
import io
import os
import json

from config import settings
from logging_config import get_logger
from code_agent import WatchFaceCodeAgent
from models import (
    AssetType,
    AssetFile,
    WatchfaceAssets,
    WatchfaceConfig,
    ProjectMetadata,
    ConversationItem,
    GenerateProjectRequest,
    EditProjectRequest,
    ProjectFile,
    GenerateProjectResponse
)
from generators import WatchfaceProjectGenerator
from utils import save_project, load_project, generate_unique_filename, list_projects, load_project_with_conversation
from utils.storage import get_upload_path, delete_project, delete_all_projects
from utils.api_key_manager import api_key_manager

# Initialize logger
logger = get_logger()

# 默认Code Agent（使用系统配置的API Key）
default_code_agent = None

def get_code_agent_for_client(client_id: Optional[str] = None) -> WatchFaceCodeAgent:
    """
    根据客户端ID获取对应的Code Agent实例
    
    Args:
        client_id: 客户端ID（从请求header中获取）
        
    Returns:
        WatchFaceCodeAgent实例
    """
    global default_code_agent
    
    if client_id:
        # 尝试获取客户端设置的API Key
        api_key = api_key_manager.get_api_key(client_id)
        
        if api_key:
            # 使用客户端的API Key创建专属agent
            logger.info(f"🔑 使用客户端API Key: {client_id[:16]}...")
            return WatchFaceCodeAgent(api_key=api_key, client_id=client_id)
    
    # 使用默认API Key
    if default_code_agent is None:
        logger.info(f"🔑 使用默认API Key")
        default_code_agent = WatchFaceCodeAgent()
    
    return default_code_agent

# Create FastAPI app
app = FastAPI(
    title="WatchFace Code Agent",
    version="2.0.0",
    description="AI-powered watchface code generation with HTML/CSS/JS"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= 基础接口 =============

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "WatchFace Code Agent Backend is running!",
        "version": "2.0.0",
        "description": "生成标准 HTML/CSS/JS 表盘代码",
        "endpoints": {
            "upload_asset": "POST /api/upload-asset",
            "generate_project": "POST /api/generate-project",
            "edit_project": "POST /api/edit-project",
            "download_project": "GET /api/download-project/{project_id}",
            "get_session": "GET /api/session/{session_id}"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_status": "ready"
    }


# ============= 素材上传接口 =============

@app.post("/api/upload-asset")
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    session_id: str = Form(...)
):
    """
    上传素材文件
    
    Args:
        file: 上传的文件
        asset_type: 素材类型
        session_id: 会话ID
    """
    logger.info(f"📤 接收素材上传请求")
    logger.info(f"   文件名: {file.filename}")
    logger.info(f"   素材类型: {asset_type}")
    logger.info(f"   会话ID: {session_id}")
    
    try:
        # 验证文件格式
        if not file.filename:
            raise HTTPException(400, "文件名不能为空")
        
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(400, f"不支持的文件格式，仅支持: {allowed_extensions}")
        
        # 生成存储文件名
        stored_filename = generate_unique_filename(file.filename, asset_type)
        
        # 保存文件
        file_path = get_upload_path(session_id, stored_filename)
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 创建AssetFile对象
        asset_file = AssetFile(
            asset_type=AssetType(asset_type),
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            mime_type=file.content_type or "image/png"
        )
        
        logger.info(f"✅ 素材上传成功: {stored_filename}")
        
        return {
            "success": True,
            "asset": asset_file.dict(),
            "message": "素材上传成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 素材上传失败: {str(e)}")
        raise HTTPException(500, f"素材上传失败: {str(e)}")


@app.post("/api/upload-batch-assets")
async def upload_batch_assets(
    file: UploadFile = File(...),
    asset_category: str = Form(...),
    session_id: str = Form(...)
):
    """
    批量上传素材文件（ZIP格式）
    
    Args:
        file: 上传的ZIP文件
        asset_category: 素材类别 (digits 或 week_images)
        session_id: 会话ID
    """
    logger.info(f"📦 接收批量素材上传请求")
    logger.info(f"   文件名: {file.filename}")
    logger.info(f"   素材类别: {asset_category}")
    logger.info(f"   会话ID: {session_id}")
    
    try:
        import zipfile
        import tempfile
        import re
        
        # 验证文件格式
        if not file.filename:
            raise HTTPException(400, "文件名不能为空")
        
        if not file.filename.lower().endswith('.zip'):
            raise HTTPException(400, "仅支持ZIP格式的压缩包")
        
        # 验证素材类别
        if asset_category not in ['digits', 'week_images']:
            raise HTTPException(400, f"不支持的素材类别: {asset_category}")
        
        uploaded_assets = []
        
        # 创建临时文件保存ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            shutil.copyfileobj(file.file, temp_zip)
            temp_zip_path = temp_zip.name
        
        try:
            # 解压ZIP文件
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                # 获取ZIP中的所有文件
                file_list = zip_ref.namelist()
                logger.info(f"   ZIP包含 {len(file_list)} 个文件")
                
                for zip_filename in file_list:
                    # 跳过目录和隐藏文件
                    if zip_filename.endswith('/') or zip_filename.startswith('.') or '/' in zip_filename[:-1]:
                        continue
                    
                    # 提取文件名（去除路径）
                    base_filename = os.path.basename(zip_filename)
                    
                    # 根据类别解析文件名
                    asset_type = None
                    if asset_category == 'digits':
                        # 匹配 digit_0 到 digit_9
                        match = re.match(r'digit_(\d)\.', base_filename, re.IGNORECASE)
                        if match and 0 <= int(match.group(1)) <= 9:
                            asset_type = f"digit_{match.group(1)}"
                    elif asset_category == 'week_images':
                        # 匹配 week_1 到 week_7
                        match = re.match(r'week_(\d)\.', base_filename, re.IGNORECASE)
                        if match and 1 <= int(match.group(1)) <= 7:
                            asset_type = f"week_{match.group(1)}"
                    
                    if not asset_type:
                        logger.warning(f"   跳过不符合命名规则的文件: {base_filename}")
                        continue
                    
                    # 验证图片格式
                    allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
                    if not any(base_filename.lower().endswith(ext) for ext in allowed_extensions):
                        logger.warning(f"   跳过不支持的文件格式: {base_filename}")
                        continue
                    
                    # 提取并保存文件
                    file_data = zip_ref.read(zip_filename)
                    
                    # 生成存储文件名
                    stored_filename = generate_unique_filename(base_filename, asset_type)
                    
                    # 保存文件
                    file_path = get_upload_path(session_id, stored_filename)
                    file_path.write_bytes(file_data)
                    
                    # 创建AssetFile对象
                    asset_file = AssetFile(
                        asset_type=AssetType(asset_type),
                        filename=base_filename,
                        stored_filename=stored_filename,
                        file_path=str(file_path),
                        file_size=len(file_data),
                        mime_type="image/png"  # 默认类型
                    )
                    
                    uploaded_assets.append(asset_file.dict())
                    logger.info(f"   ✓ 成功上传: {base_filename} -> {asset_type}")
        
        finally:
            # 清理临时ZIP文件
            try:
                os.unlink(temp_zip_path)
            except:
                pass
        
        if not uploaded_assets:
            raise HTTPException(400, "ZIP包中没有找到符合命名规则的文件")
        
        logger.info(f"✅ 批量上传成功，共上传 {len(uploaded_assets)} 个文件")
        
        return {
            "success": True,
            "assets": uploaded_assets,
            "count": len(uploaded_assets),
            "message": f"成功上传 {len(uploaded_assets)} 个文件"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 批量素材上传失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"批量素材上传失败: {str(e)}")


# ============= 项目生成接口 =============

@app.post("/api/generate-project", response_model=GenerateProjectResponse)
async def generate_project(
    request: GenerateProjectRequest,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    生成新的表盘项目
    
    Args:
        request: 生成项目请求
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"🎨 接收生成项目请求")
    logger.info(f"   指令: {request.instruction}")
    logger.info(f"   会话ID: {request.session_id}")
    logger.info(f"   客户端ID: {x_client_id[:16] if x_client_id else 'None'}...")
    
    try:
        # 根据客户端ID获取对应的Code Agent
        code_agent = get_code_agent_for_client(x_client_id)
        
        # 创建项目元数据
        metadata = ProjectMetadata(
            project_id=str(uuid.uuid4()),
            session_id=request.session_id,
            client_id=x_client_id or "default",  # 保存客户端ID
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            config=request.config or WatchfaceConfig(),
            assets=request.assets,
            last_instruction=request.instruction
        )
        
        logger.info(f"   项目ID: {metadata.project_id}")
        logger.info(f"   项目名称: {metadata.config.watchface_name}")
        
        # 调用Code Agent生成 HTML 代码
        result = await code_agent.process_instruction(
            user_input=request.instruction,
            current_code=None,
            conversation_history=[],
            assets=metadata.assets,
            config=metadata.config
        )
        
        if not result.get("success"):
            raise HTTPException(500, result.get("message", "代码生成失败"))
        
        html_content = result.get("code", "")
        
        # 生成完整项目结构
        generator = WatchfaceProjectGenerator(metadata)
        files = generator.generate_file_structure(html_content)
        file_tree = generator.generate_file_tree(files)
        
        # 添加对话历史（保留agent完整的生成内容）
        assistant_message = result.get("message", "✅ 项目生成成功")
        
        # 构建完整的assistant回复内容
        assistant_full_content = f"{assistant_message}\n\n"
        if result.get("stats"):
            stats = result.get("stats")
            assistant_full_content += f"📊 代码统计：{stats.get('lines', 0)}行 | {stats.get('characters', 0)}字符"
        
        conversation_history = [
            ConversationItem(
                role="user",
                content=request.instruction,
                timestamp=datetime.now().isoformat()
            ),
            ConversationItem(
                role="assistant",
                content=assistant_full_content.strip(),  # 保存完整的assistant回复内容
                timestamp=datetime.now().isoformat(),
                reasoning=result.get("reasoning", ""),  # 思考过程
                raw_content=result.get("raw_content", ""),  # 🆕 Agent返回的完整原始内容
                code_snapshot=html_content[:500] if html_content else "",  # 代码快照
                full_message=result.get("message", "")  # 原始message
            )
        ]
        metadata.conversation_history = conversation_history
        metadata.generation_count = 1
        
        # 保存项目
        await save_project(metadata.project_id, files, metadata)
        
        # 构建响应
        file_list = [
            ProjectFile(
                path=path,
                content=content,
                language=generator.detect_language(path)
            )
            for path, content in files.items()
            if content != "[BINARY_FILE]"
        ]
        
        logger.info(f"✅ 项目生成成功")
        logger.info(f"   文件数: {len(file_list)}")
        
        return GenerateProjectResponse(
            project_id=metadata.project_id,
            files=file_list,
            file_tree=file_tree,
            reasoning=result.get("reasoning", ""),
            success=True,
            message="项目生成成功",
            conversation_history=[item.dict() for item in metadata.conversation_history]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 项目生成失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"项目生成失败: {str(e)}")


# ============= 项目编辑接口 =============

@app.post("/api/edit-project", response_model=GenerateProjectResponse)
async def edit_project(
    request: EditProjectRequest,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    编辑现有项目
    
    Args:
        request: 编辑项目请求
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"✏️ 接收编辑项目请求")
    logger.info(f"   项目ID: {request.project_id}")
    logger.info(f"   指令: {request.instruction}")
    logger.info(f"   客户端ID: {x_client_id[:16] if x_client_id else 'None'}...")
    
    try:
        # 根据客户端ID获取对应的Code Agent
        code_agent = get_code_agent_for_client(x_client_id)
        # 加载现有项目
        project_data = await load_project(request.project_id)
        if not project_data:
            raise HTTPException(404, "项目不存在")
        
        # 获取当前index.html
        metadata_dict = project_data["metadata"]
        files = project_data["files"]
        
        # 验证权限：检查项目是否属于当前客户端
        project_client_id = metadata_dict.get("client_id", "default")
        current_client_id = x_client_id or "default"
        if project_client_id != current_client_id:
            logger.warning(f"⚠️ 客户端 {current_client_id} 尝试访问客户端 {project_client_id} 的项目")
            raise HTTPException(403, "无权访问此项目")
        
        logger.info(f"✅ 权限验证通过: 客户端 {current_client_id}")
        
        # 查找 HTML 文件
        html_key = "index.html"
        
        if html_key not in files:
            raise HTTPException(404, "index.html 文件不存在")
        
        current_html = files[html_key]
        
        # 转换metadata为ProjectMetadata对象以获取assets和config
        from models.project import ProjectMetadata
        metadata = ProjectMetadata(**metadata_dict)
        
        # 合并新上传的素材（如果有）
        if request.assets:
            # 将新素材合并到现有素材中
            if metadata.assets:
                # 更新现有素材
                if request.assets.background_round:
                    metadata.assets.background_round = request.assets.background_round
                if request.assets.background_square:
                    metadata.assets.background_square = request.assets.background_square
                if request.assets.pointer_hour:
                    metadata.assets.pointer_hour = request.assets.pointer_hour
                if request.assets.pointer_minute:
                    metadata.assets.pointer_minute = request.assets.pointer_minute
                if request.assets.pointer_second:
                    metadata.assets.pointer_second = request.assets.pointer_second
                if request.assets.digits:
                    metadata.assets.digits = request.assets.digits
                if request.assets.week_images:
                    metadata.assets.week_images = request.assets.week_images
                if request.assets.decorations:
                    metadata.assets.decorations = request.assets.decorations
            else:
                # 如果之前没有素材，直接使用新素材
                metadata.assets = request.assets
        
        # 获取对话历史
        conversation_history = metadata_dict.get("conversation_history", [])
        
        # 调用Code Agent编辑
        result = await code_agent.process_instruction(
            user_input=request.instruction,
            current_code=current_html,
            conversation_history=conversation_history,
            assets=metadata.assets,  # 使用合并后的素材
            config=metadata.config
        )
        
        if not result.get("success"):
            raise HTTPException(500, result.get("message", "代码编辑失败"))
        
        new_html = result.get("code", current_html)
        
        # 更新项目文件
        files[html_key] = new_html
        metadata_dict["updated_at"] = datetime.now().isoformat()
        metadata_dict["generation_count"] = metadata_dict.get("generation_count", 0) + 1
        metadata_dict["last_instruction"] = request.instruction
        
        # 确保 client_id 存在（兼容旧项目）
        if "client_id" not in metadata_dict or not metadata_dict["client_id"]:
            metadata_dict["client_id"] = current_client_id
        
        # 更新metadata中的assets（确保新素材被保存）
        if metadata.assets:
            metadata_dict["assets"] = metadata.assets.dict()
        
        # 追加对话历史（保留agent完整的生成内容）
        assistant_message = result.get("message", "✅ 项目编辑成功")
        
        # 如果message中包含详细信息，保留完整内容
        assistant_full_content = f"{assistant_message}\n\n"
        
        # 处理diff信息（如果有）
        if result.get("diff"):
            diff_data = result.get("diff")
            if isinstance(diff_data, dict):
                total_changes = diff_data.get("total_changes", 0)
                added_count = len(diff_data.get("added_lines", []))
                removed_count = len(diff_data.get("removed_lines", []))
                assistant_full_content += f"📝 代码变更：+{added_count}行 -{removed_count}行（共{total_changes}处修改）\n\n"
        
        # 处理统计信息
        if result.get("stats"):
            stats = result.get("stats")
            assistant_full_content += f"📊 代码统计：{stats.get('lines', 0)}行 | {stats.get('characters', 0)}字符"
        
        new_conversation = [
            {
                "role": "user",
                "content": request.instruction,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant",
                "content": assistant_full_content.strip(),  # 保存完整的assistant回复内容
                "timestamp": datetime.now().isoformat(),
                "reasoning": result.get("reasoning", ""),  # 思考过程
                "raw_content": result.get("raw_content", ""),  # 🆕 Agent返回的完整原始内容
                "code_snapshot": new_html[:500] if new_html else "",  # 代码快照
                "full_message": result.get("message", "")  # 原始message
            }
        ]
        conversation_history.extend(new_conversation)
        metadata_dict["conversation_history"] = conversation_history
        
        # 保存项目
        await save_project(request.project_id, files, metadata_dict)
        
        # 重新构建metadata对象用于generator
        metadata = ProjectMetadata(**metadata_dict)
        generator = WatchfaceProjectGenerator(metadata)
        file_tree = generator.generate_file_tree(files)
        
        # 构建响应
        file_list = [
            ProjectFile(
                path=path,
                content=content,
                language=generator.detect_language(path)
            )
            for path, content in files.items()
            if content != "[BINARY_FILE]"
        ]
        
        logger.info(f"✅ 项目编辑成功")
        
        return GenerateProjectResponse(
            project_id=request.project_id,
            files=file_list,
            file_tree=file_tree,
            reasoning=result.get("reasoning", ""),
            success=True,
            message="项目编辑成功",
            conversation_history=conversation_history  # 返回更新后的对话历史
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 项目编辑失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"项目编辑失败: {str(e)}")


# ============= 项目下载接口 =============

@app.get("/api/download-project/{project_id}")
async def download_project(
    project_id: str,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    下载项目ZIP包（验证权限）
    
    Args:
        project_id: 项目ID
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"📦 接收项目下载请求: {project_id}")
    current_client_id = x_client_id or "default"
    logger.info(f"   客户端ID: {current_client_id}")
    
    try:
        # 加载项目
        project_data = await load_project(project_id)
        if not project_data:
            raise HTTPException(404, "项目不存在")
        
        metadata = project_data["metadata"]
        files = project_data["files"]
        
        # 验证权限
        project_client_id = metadata.get("client_id", "default")
        if project_client_id != current_client_id:
            logger.warning(f"⚠️ 客户端 {current_client_id} 尝试下载客户端 {project_client_id} 的项目")
            raise HTTPException(403, "无权下载此项目")
        
        # 创建内存ZIP文件
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加文本文件
            for file_path, content in files.items():
                if content != "[BINARY_FILE]":
                    zipf.writestr(f"src/{file_path}", content)
                else:
                    # 添加二进制素材文件
                    session_id = metadata["session_id"]
                    filename = Path(file_path).name
                    asset_path = get_upload_path(session_id, filename)
                    
                    if asset_path.exists():
                        zipf.write(asset_path, f"src/{file_path}")
        
        zip_buffer.seek(0)
        
        # 生成文件名
        watchface_name = metadata["config"]["watchface_name"]
        filename = f"{watchface_name}.zip"
        
        logger.info(f"✅ 项目打包成功: {filename}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 项目下载失败: {str(e)}")
        raise HTTPException(500, f"项目下载失败: {str(e)}")


# ============= 会话管理接口 =============

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    获取会话状态
    
    Args:
        session_id: 会话ID
    """
    logger.info(f"📊 获取会话状态: {session_id}")
    
    try:
        # 这里可以返回会话的项目列表等信息
        # 简化版本只返回基本信息
        return {
            "session_id": session_id,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 获取会话失败: {str(e)}")
        raise HTTPException(500, f"获取会话失败: {str(e)}")


# ============= 项目列表接口 =============

@app.get("/api/projects")
async def get_projects(
    session_id: Optional[str] = None,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    获取历史项目列表（按客户端ID过滤）
    
    Args:
        session_id: 可选的会话ID，如果提供则只返回该会话的项目
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"📋 获取项目列表")
    current_client_id = x_client_id or "default"
    logger.info(f"   客户端ID: {current_client_id}")
    if session_id:
        logger.info(f"   会话ID过滤: {session_id}")
    
    try:
        # 获取所有项目
        all_projects = await list_projects(session_id)
        
        # 按客户端ID过滤项目
        filtered_projects = []
        for project in all_projects:
            project_client_id = project.get("client_id", "default")
            if project_client_id == current_client_id:
                filtered_projects.append(project)
        
        logger.info(f"✅ 客户端 {current_client_id} 的项目数: {len(filtered_projects)} (总数: {len(all_projects)})")
        
        return {
            "success": True,
            "projects": filtered_projects,
            "total": len(filtered_projects)
        }
        
    except Exception as e:
        logger.error(f"❌ 获取项目列表失败: {str(e)}")
        raise HTTPException(500, f"获取项目列表失败: {str(e)}")


# ============= 删除项目接口 =============

@app.delete("/api/project/{project_id}")
async def delete_project_api(
    project_id: str,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    删除单个项目（验证权限）
    
    Args:
        project_id: 项目ID
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"🗑️ 删除项目请求: {project_id}")
    current_client_id = x_client_id or "default"
    logger.info(f"   客户端ID: {current_client_id}")
    
    try:
        # 先加载项目验证权限
        project_data = await load_project(project_id)
        if not project_data:
            raise HTTPException(404, "项目不存在")
        
        # 验证权限
        metadata = project_data["metadata"]
        project_client_id = metadata.get("client_id", "default")
        if project_client_id != current_client_id:
            logger.warning(f"⚠️ 客户端 {current_client_id} 尝试删除客户端 {project_client_id} 的项目")
            raise HTTPException(403, "无权删除此项目")
        
        # 执行删除
        success = await delete_project(project_id)
        
        if not success:
            raise HTTPException(500, "删除失败")
        
        logger.info(f"✅ 项目已删除: {project_id}")
        
        return {
            "success": True,
            "message": "项目已成功删除",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除项目失败: {str(e)}")
        raise HTTPException(500, f"删除项目失败: {str(e)}")


@app.delete("/api/projects")
async def delete_all_projects_api(session_id: Optional[str] = None):
    """
    删除所有项目或指定会话的所有项目
    
    Args:
        session_id: 可选的会话ID，如果提供则只删除该会话的项目
    """
    scope = f"会话 {session_id}" if session_id else "所有"
    logger.info(f"🗑️ 批量删除项目请求: {scope}")
    
    try:
        result = await delete_all_projects(session_id)
        
        logger.info(f"✅ 批量删除完成: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 批量删除项目失败: {str(e)}")
        raise HTTPException(500, f"批量删除项目失败: {str(e)}")


# ============= 素材管理接口 =============

@app.delete("/api/asset/{session_id}/{filename}")
async def delete_asset(session_id: str, filename: str):
    """
    删除指定的素材文件
    
    Args:
        session_id: 会话ID
        filename: 文件名（stored_filename）
    """
    logger.info(f"🗑️ 删除素材请求: {filename} (会话: {session_id})")
    
    try:
        from pathlib import Path
        from utils.storage import UPLOADS_DIR
        
        # 构建文件路径
        file_path = UPLOADS_DIR / session_id / filename
        
        if not file_path.exists():
            logger.warning(f"⚠️ 文件不存在: {file_path}")
            raise HTTPException(404, "素材文件不存在")
        
        # 删除文件
        file_path.unlink()
        
        logger.info(f"✅ 素材删除成功: {filename}")
        
        return {
            "success": True,
            "message": "素材删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除素材失败: {str(e)}")
        raise HTTPException(500, f"删除素材失败: {str(e)}")


@app.delete("/api/assets/{session_id}")
async def delete_all_assets(session_id: str):
    """
    删除会话的所有素材文件（用于切换项目或新建项目时清空）
    
    Args:
        session_id: 会话ID
    """
    logger.info(f"🗑️ 删除会话所有素材: {session_id}")
    
    try:
        from pathlib import Path
        from utils.storage import UPLOADS_DIR
        import shutil
        
        # 构建会话目录
        session_dir = UPLOADS_DIR / session_id
        
        if session_dir.exists():
            # 删除整个目录
            shutil.rmtree(session_dir)
            logger.info(f"✅ 会话素材目录已删除: {session_dir}")
        else:
            logger.info(f"⚠️ 会话素材目录不存在: {session_dir}")
        
        return {
            "success": True,
            "message": "素材清空成功"
        }
        
    except Exception as e:
        logger.error(f"❌ 清空素材失败: {str(e)}")
        raise HTTPException(500, f"清空素材失败: {str(e)}")


# ============= 项目素材访问接口 =============

@app.get("/api/project/{project_id}/assets/{filename}")
async def get_project_asset(project_id: str, filename: str):
    """
    获取项目素材文件
    
    Args:
        project_id: 项目ID
        filename: 文件名
    """
    try:
        from pathlib import Path
        from fastapi.responses import FileResponse
        import mimetypes
        
        # 使用绝对路径构建素材文件路径
        from utils.storage import PROJECTS_DIR
        asset_path = PROJECTS_DIR / project_id / "src" / "assets" / filename
        
        logger.info(f"📂 请求素材文件: {asset_path}")
        
        if not asset_path.exists():
            logger.warning(f"⚠️ 素材文件不存在: {asset_path}")
            raise HTTPException(404, "素材文件不存在")
        
        # 根据文件扩展名动态设置MIME类型
        mime_type, _ = mimetypes.guess_type(str(asset_path))
        if not mime_type:
            mime_type = "image/png"  # 默认类型
        
        logger.info(f"✅ 返回素材文件: {filename} ({mime_type})")
        
        # 返回文件
        return FileResponse(
            path=str(asset_path),
            media_type=mime_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取素材文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"获取素材文件失败: {str(e)}")


# ============= 获取单个项目接口 =============

@app.get("/api/project/{project_id}")
async def get_project(
    project_id: str,
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID")
):
    """
    获取单个项目详情（包含对话历史，验证权限）
    
    Args:
        project_id: 项目ID
        x_client_id: 客户端ID（从header获取）
    """
    logger.info(f"📂 获取项目详情: {project_id}")
    current_client_id = x_client_id or "default"
    logger.info(f"   客户端ID: {current_client_id}")
    
    try:
        project_data = await load_project_with_conversation(project_id)
        
        if not project_data:
            raise HTTPException(404, "项目不存在")
        
        metadata = project_data["metadata"]
        files = project_data["files"]
        conversation = project_data.get("conversation", [])
        
        # 验证权限
        project_client_id = metadata.get("client_id", "default")
        if project_client_id != current_client_id:
            logger.warning(f"⚠️ 客户端 {current_client_id} 尝试访问客户端 {project_client_id} 的项目")
            raise HTTPException(403, "无权访问此项目")
        
        logger.info(f"📝 对话历史数量: {len(conversation)}")
        if len(conversation) > 0:
            logger.info(f"   第一条: {conversation[0].get('role')} - {conversation[0].get('content', '')[:50]}")
        else:
            logger.warning("⚠️ 对话历史为空！")
            logger.info(f"   metadata中的conversation_history字段: {'conversation_history' in metadata}")
            if 'conversation_history' in metadata:
                logger.info(f"   metadata.conversation_history长度: {len(metadata.get('conversation_history', []))}")
        
        # 生成文件树
        from models.project import WatchfaceConfig, ProjectMetadata
        config = WatchfaceConfig(**metadata["config"])
        metadata_obj = ProjectMetadata(**metadata)
        generator = WatchfaceProjectGenerator(metadata_obj)
        file_tree = generator.generate_file_tree(files)
        
        # 构建文件列表
        file_list = [
            ProjectFile(
                path=path,
                content=content,
                language=generator.detect_language(path)
            )
            for path, content in files.items()
            if content != "[BINARY_FILE]"
        ]
        
        logger.info(f"✅ 项目加载成功: {metadata.get('config', {}).get('watchface_name', '未命名')}")
        
        return {
            "success": True,
            "project_id": project_id,
            "metadata": metadata,
            "files": [f.dict() for f in file_list],
            "file_tree": file_tree,
            "conversation": conversation,
            "config": metadata.get("config"),
            "assets": metadata.get("assets")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取项目详情失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"获取项目详情失败: {str(e)}")


# ============= API Key管理接口 =============

class SetApiKeyRequest(BaseModel):
    """设置API Key请求"""
    client_id: str
    api_key: str


class TestApiKeyRequest(BaseModel):
    """测试API Key请求"""
    api_key: str


@app.post("/api/set-api-key")
async def set_api_key_endpoint(request: SetApiKeyRequest):
    """
    设置客户端的API Key
    
    Args:
        request: API Key设置请求
    """
    logger.info(f"🔑 设置API Key: 客户端 {request.client_id[:16]}...")
    
    try:
        result = api_key_manager.set_api_key(request.client_id, request.api_key)
        logger.info(f"✅ API Key设置{'成功' if result['success'] else '失败'}")
        return result
    except Exception as e:
        logger.error(f"❌ 设置API Key失败: {str(e)}")
        raise HTTPException(500, f"设置API Key失败: {str(e)}")


@app.get("/api/get-api-key")
async def get_api_key_endpoint(client_id: str):
    """
    获取客户端API Key的状态
    
    Args:
        client_id: 客户端ID
    """
    logger.info(f"🔍 查询API Key状态: 客户端 {client_id[:16]}...")
    
    try:
        status = api_key_manager.has_api_key(client_id)
        logger.info(f"   状态: {'已设置' if status.get('has_key') else '未设置'}")
        return status
    except Exception as e:
        logger.error(f"❌ 查询API Key状态失败: {str(e)}")
        raise HTTPException(500, f"查询失败: {str(e)}")


@app.post("/api/test-api-key")
async def test_api_key_endpoint(request: TestApiKeyRequest):
    """
    测试API Key是否有效
    
    Args:
        request: 测试请求
    """
    logger.info(f"🧪 测试API Key有效性...")
    
    try:
        # 简单测试：尝试创建一个临时的客户端
        from openai import AsyncOpenAI
        import os
        
        test_client = AsyncOpenAI(
            base_url=os.getenv('MINIMAX_BASE_URL', 'https://api.minimaxi.com/v1'),
            api_key=request.api_key
        )
        
        # 发送一个简单的测试请求
        response = await test_client.chat.completions.create(
            model="MiniMax-Text-01",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=10
        )
        
        logger.info(f"✅ API Key验证成功")
        return {
            "success": True,
            "message": "API Key验证成功",
            "model": response.model
        }
    except Exception as e:
        logger.error(f"❌ API Key验证失败: {str(e)}")
        return {
            "success": False,
            "message": f"验证失败: {str(e)}"
        }


# ============= 启动应用 =============

if __name__ == "__main__":
    logger.info(f"🚀 启动表盘 Code Agent 后端服务")
    logger.info(f"   监听地址: {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
