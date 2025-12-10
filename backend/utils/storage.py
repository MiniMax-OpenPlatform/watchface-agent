"""
存储相关工具函数
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


# 存储目录
STORAGE_ROOT = Path(__file__).parent.parent.parent / "storage"
PROJECTS_DIR = STORAGE_ROOT / "projects"
UPLOADS_DIR = STORAGE_ROOT / "uploads"

# 确保目录存在
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def generate_unique_filename(original_filename: str, asset_type: str) -> str:
    """
    生成唯一的文件名
    
    Args:
        original_filename: 原始文件名
        asset_type: 素材类型
        
    Returns:
        唯一的文件名
    """
    # 获取文件扩展名
    ext = Path(original_filename).suffix
    
    # 生成唯一前缀（使用asset_type + 时间戳）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_prefix = f"{asset_type}_{timestamp}"
    
    # 组合文件名
    return f"{unique_prefix}{ext}"


async def save_project(
    project_id: str,
    files: Dict[str, str],
    metadata: Any
) -> bool:
    """
    保存项目到存储 - 将代码写入实际文件系统
    
    Args:
        project_id: 项目ID
        files: 文件字典 (路径 -> 内容)
        metadata: 项目元数据
        
    Returns:
        是否成功
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        src_dir = project_dir / "src"
        assets_dir = src_dir / "assets"
        src_dir.mkdir(parents=True, exist_ok=True)
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 保存元数据（不包含文件内容）
        metadata_path = project_dir / "metadata.json"
        with metadata_path.open('w', encoding='utf-8') as f:
            if hasattr(metadata, 'dict'):
                json.dump(metadata.dict(), f, ensure_ascii=False, indent=2)
            else:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 2. 复制素材文件到项目assets目录
        session_id = None
        if hasattr(metadata, 'session_id'):
            session_id = metadata.session_id
        elif isinstance(metadata, dict) and 'session_id' in metadata:
            session_id = metadata['session_id']
        
        if session_id:
            # 获取素材信息
            assets = None
            if hasattr(metadata, 'assets'):
                assets = metadata.assets
            elif isinstance(metadata, dict) and 'assets' in metadata:
                assets = metadata['assets']
            
            if assets:
                # 从assets对象中收集所有素材文件
                from models.assets import WatchfaceAssets
                if isinstance(assets, dict):
                    assets_obj = WatchfaceAssets(**assets)
                else:
                    assets_obj = assets
                
                # 获取所有素材的文件名
                all_asset_files = assets_obj.get_all_filenames()
                
                # 复制素材文件
                upload_dir = UPLOADS_DIR / session_id
                for asset_filename in all_asset_files:
                    src_file = upload_dir / asset_filename
                    if src_file.exists():
                        dest_file = assets_dir / asset_filename
                        import shutil
                        shutil.copy2(src_file, dest_file)
                        print(f"  ✓ 复制素材: {asset_filename}")
        
        # 3. 将每个文件写入实际文件系统
        for file_path, content in files.items():
            # 跳过二进制文件标记（已在上面处理）
            if content == "[BINARY_FILE]":
                continue
            
            # 构建完整路径
            full_path = src_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with full_path.open('w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ 项目已保存到文件系统: {project_dir}")
        return True
        
    except Exception as e:
        print(f"❌ 保存项目失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def load_project(project_id: str) -> Optional[Dict[str, Any]]:
    """
    加载项目 - 从文件系统读取代码文件
    
    Args:
        project_id: 项目ID
        
    Returns:
        项目数据字典或None
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        src_dir = project_dir / "src"
        
        if not project_dir.exists():
            return None
        
        # 1. 加载元数据
        metadata_path = project_dir / "metadata.json"
        if not metadata_path.exists():
            return None
        
        with metadata_path.open('r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 2. 从文件系统读取所有代码文件
        files = {}
        
        # 尝试从新的 src/ 目录读取
        if src_dir.exists():
            for file_path in src_dir.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    relative_path = str(file_path.relative_to(src_dir))
                    
                    # 读取文件内容
                    try:
                        with file_path.open('r', encoding='utf-8') as f:
                            files[relative_path] = f.read()
                    except UnicodeDecodeError:
                        # 二进制文件
                        files[relative_path] = "[BINARY_FILE]"
        else:
            # 向后兼容：如果没有 src/ 目录，尝试读取旧的 files.json
            files_path = project_dir / "files.json"
            if files_path.exists():
                with files_path.open('r', encoding='utf-8') as f:
                    files = json.load(f)
                print(f"⚠️  从旧格式 files.json 加载项目: {project_id}")
        
        return {
            "metadata": metadata,
            "files": files
        }
        
    except Exception as e:
        print(f"❌ 加载项目失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_upload_path(session_id: str, filename: str) -> Path:
    """
    获取上传文件的完整路径
    
    Args:
        session_id: 会话ID
        filename: 文件名
        
    Returns:
        文件路径
    """
    session_dir = UPLOADS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / filename


async def list_projects(session_id: Optional[str] = None) -> list:
    """
    获取项目列表
    
    Args:
        session_id: 可选的会话ID，如果提供则只返回该会话的项目
        
    Returns:
        项目列表
    """
    projects = []
    
    try:
        if not PROJECTS_DIR.exists():
            return projects
        
        for project_dir in PROJECTS_DIR.iterdir():
            if not project_dir.is_dir():
                continue
            
            metadata_path = project_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            
            try:
                with metadata_path.open('r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 如果指定了session_id，只返回该会话的项目
                if session_id and metadata.get("session_id") != session_id:
                    continue
                
                projects.append({
                    "project_id": project_dir.name,
                    "session_id": metadata.get("session_id", ""),
                    "watchface_name": metadata.get("config", {}).get("watchface_name", "未命名"),
                    "created_at": metadata.get("created_at", ""),
                    "updated_at": metadata.get("updated_at", ""),
                    "last_instruction": metadata.get("last_instruction", ""),
                    "generation_count": metadata.get("generation_count", 1),
                })
            except Exception:
                continue
        
        # 按更新时间排序（最新的在前面）
        projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
    except Exception as e:
        print(f"获取项目列表失败: {e}")
    
    return projects


async def load_project_with_conversation(project_id: str) -> Optional[Dict[str, Any]]:
    """
    加载项目（包含完整对话历史）
    
    Args:
        project_id: 项目ID
        
    Returns:
        项目数据字典或None（包含对话历史）
    """
    project_data = await load_project(project_id)
    if not project_data:
        return None
    
    # 从元数据中提取对话历史
    metadata = project_data["metadata"]
    
    # 优先使用保存的完整对话历史
    conversation = metadata.get("conversation_history", [])
    
    # 如果没有对话历史（旧项目），用last_instruction重建一条（向后兼容）
    if not conversation and metadata.get("last_instruction"):
        conversation = [
            {
                "role": "user",
                "content": metadata["last_instruction"],
                "timestamp": metadata.get("created_at", ""),
            },
            {
                "role": "assistant",
                "content": "✅ 项目生成成功",
                "timestamp": metadata.get("updated_at", ""),
            }
        ]
    
    project_data["conversation"] = conversation
    
    return project_data


async def delete_project(project_id: str) -> bool:
    """
    删除单个项目
    
    Args:
        project_id: 项目ID
        
    Returns:
        是否成功
    """
    try:
        project_dir = PROJECTS_DIR / project_id
        if not project_dir.exists():
            print(f"⚠️ 项目不存在: {project_id}")
            return False
        
        # 删除整个项目目录
        import shutil
        shutil.rmtree(project_dir)
        print(f"✅ 项目已删除: {project_id}")
        return True
        
    except Exception as e:
        print(f"❌ 删除项目失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def delete_all_projects(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    删除所有项目或指定会话的所有项目
    
    Args:
        session_id: 会话ID（可选，如果提供则只删除该会话的项目）
        
    Returns:
        删除结果字典
    """
    try:
        deleted_count = 0
        failed_count = 0
        
        if not PROJECTS_DIR.exists():
            return {
                "success": True,
                "deleted_count": 0,
                "failed_count": 0,
                "message": "项目目录不存在"
            }
        
        for project_dir in PROJECTS_DIR.iterdir():
            if not project_dir.is_dir():
                continue
            
            # 如果指定了session_id，只删除该会话的项目
            if session_id:
                metadata_path = project_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with metadata_path.open('r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        if metadata.get("session_id") != session_id:
                            continue
                    except:
                        continue
            
            # 删除项目目录
            try:
                import shutil
                shutil.rmtree(project_dir)
                deleted_count += 1
                print(f"  ✓ 已删除: {project_dir.name}")
            except Exception as e:
                failed_count += 1
                print(f"  ✗ 删除失败: {project_dir.name} - {e}")
        
        message = f"成功删除 {deleted_count} 个项目"
        if failed_count > 0:
            message += f"，{failed_count} 个项目删除失败"
        
        print(f"✅ {message}")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "message": message
        }
        
    except Exception as e:
        print(f"❌ 批量删除项目失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "deleted_count": 0,
            "failed_count": 0,
            "message": f"批量删除失败: {str(e)}"
        }

