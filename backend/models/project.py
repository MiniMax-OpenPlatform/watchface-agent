"""
项目配置相关数据模型
"""

from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List
import re
from .assets import WatchfaceAssets


class ConversationItem(BaseModel):
    """对话记录项"""
    role: Literal["user", "assistant"] = "user"
    content: str
    timestamp: str = ""
    reasoning: Optional[str] = None  # Agent的思考过程
    code_snapshot: Optional[str] = None  # 代码快照（前500字符）
    raw_content: Optional[str] = None  # Agent返回的完整原始内容
    full_message: Optional[str] = None  # 原始message字段
    
    class Config:
        extra = "ignore"


class WatchfaceConfig(BaseModel):
    """表盘配置（简化版）"""
    watchface_name: str = Field(
        default="AI生成表盘",
        description="项目名称"
    )
    
    @validator('watchface_name')
    def validate_watchface_name(cls, v):
        """验证表盘名称"""
        if len(v) < 1 or len(v) > 50:
            raise ValueError('表盘名称长度应在1-50之间')
        return v


class ProjectMetadata(BaseModel):
    """项目元数据"""
    project_id: str                    # 项目唯一ID
    session_id: str                    # 会话ID
    client_id: Optional[str] = None    # 客户端ID（用于项目隔离）
    created_at: str                    # 创建时间
    updated_at: str                    # 更新时间
    config: WatchfaceConfig            # 项目配置
    assets: WatchfaceAssets            # 素材集合
    generation_count: int = 0          # 生成次数
    last_instruction: str = ""         # 最后一次指令
    conversation_history: List[ConversationItem] = []  # 完整对话历史
    
    class Config:
        extra = "ignore"

