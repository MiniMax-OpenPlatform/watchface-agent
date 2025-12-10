"""
API请求响应数据模型
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from .assets import WatchfaceAssets
from .project import WatchfaceConfig


class GenerateProjectRequest(BaseModel):
    """生成项目请求"""
    instruction: str                   # 用户指令
    assets: WatchfaceAssets           # 素材集合
    config: Optional[WatchfaceConfig] = None
    session_id: str                    # 会话ID


class EditProjectRequest(BaseModel):
    """编辑项目请求"""
    instruction: str                   # 编辑指令
    session_id: str                    # 会话ID
    project_id: str                    # 项目ID
    assets: Optional[WatchfaceAssets] = None  # 新上传的素材（可选）


class ProjectFile(BaseModel):
    """项目文件"""
    path: str                          # 文件路径（相对于src/）
    content: str                       # 文件内容
    language: str = "plaintext"        # 语言类型（用于代码高亮）


class FileTreeNode(BaseModel):
    """文件树节点"""
    name: str
    type: str                          # "file" or "folder"
    path: str
    children: Optional[List['FileTreeNode']] = None


# 解决循环引用
FileTreeNode.update_forward_refs()


class GenerateProjectResponse(BaseModel):
    """生成项目响应"""
    project_id: str                    # 项目ID
    files: List[ProjectFile]           # 文件列表
    file_tree: Dict[str, Any]          # 文件树结构
    reasoning: str                     # Agent思考过程
    success: bool                      # 是否成功
    message: str = ""                  # 提示信息
    conversation_history: List[Dict[str, Any]] = []  # 对话历史

