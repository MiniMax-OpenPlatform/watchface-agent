"""
提示词模块
"""

from .system_prompt import VIVO_WATCHFACE_SYSTEM_PROMPT
from .user_prompt import build_generation_prompt, build_edit_prompt

__all__ = [
    'VIVO_WATCHFACE_SYSTEM_PROMPT',
    'build_generation_prompt',
    'build_edit_prompt',
]

