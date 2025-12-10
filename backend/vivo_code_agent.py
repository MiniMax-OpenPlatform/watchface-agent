"""
vivo BlueOS表盘Code Agent核心引擎
"""

import re
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI
import difflib

from config import settings
from logging_config import get_logger
from models.assets import WatchfaceAssets
from models.project import WatchfaceConfig
from prompts import (
    VIVO_WATCHFACE_SYSTEM_PROMPT,
    build_generation_prompt,
    build_edit_prompt
)

logger = get_logger()


class VivoWatchfaceCodeAgent:
    """vivo BlueOS表盘Code Agent"""
    
    def __init__(self):
        """初始化Code Agent"""
        self.client = AsyncOpenAI(
            api_key=settings.MINIMAX_API_KEY,
            base_url=settings.MINIMAX_BASE_URL,
            timeout=180.0  # 3分钟超时
        )
        self.model = settings.MINIMAX_MODEL
        self.system_prompt = VIVO_WATCHFACE_SYSTEM_PROMPT
        self.last_reasoning = ""  # 最后一次推理过程
        
        logger.info(f"✅ vivo表盘Code Agent初始化完成")
        logger.info(f"   模型: {self.model}")
        logger.info(f"   Base URL: {settings.MINIMAX_BASE_URL}")
    
    async def generate_watchface(
        self,
        instruction: str,
        assets: WatchfaceAssets,
        config: WatchfaceConfig
    ) -> str:
        """
        生成完整的表盘index.ux代码
        
        Args:
            instruction: 用户指令
            assets: 素材集合
            config: 表盘配置
            
        Returns:
            完整的index.ux文件内容
        """
        logger.info(f"🎨 开始生成vivo表盘代码")
        logger.info(f"   指令: {instruction}")
        logger.info(f"   模式: {config.mode}")
        logger.info(f"   表盘ID: {config.watchface_id}")
        
        try:
            # 构建提示词
            user_prompt = build_generation_prompt(instruction, assets, config)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 记录请求详情
            logger.info("📤 MiniMax API 请求详情:")
            logger.info(f"   System Prompt长度: {len(self.system_prompt)}")
            logger.info(f"   User Prompt: {user_prompt[:500]}...")
            
            # 调用MiniMax-M2
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.MAX_TOKENS,
                extra_body={"reasoning_split": True}  # 获取思考过程
            )
            
            # 提取响应
            choice = response.choices[0]
            raw_content = choice.message.content
            
            # 提取reasoning（思考过程）
            reasoning_details = getattr(choice.message, 'reasoning_details', None)
            if reasoning_details:
                self.last_reasoning = " ".join([
                    detail.get('text', '') 
                    for detail in reasoning_details 
                    if isinstance(detail, dict)
                ])
            else:
                self.last_reasoning = "（无推理过程）"
            
            # 记录响应详情
            logger.info("📥 MiniMax API 响应详情:")
            logger.info(f"   模型: {response.model}")
            logger.info(f"   完成原因: {choice.finish_reason}")
            logger.info(f"   Reasoning长度: {len(self.last_reasoning)}")
            logger.info(f"   Reasoning: {self.last_reasoning[:300]}...")
            logger.info(f"   原始响应长度: {len(raw_content)}")
            logger.info(f"   原始响应: {raw_content[:500]}...")
            
            # 提取.ux代码
            ux_code = self._extract_ux_code(raw_content)
            
            # 验证代码
            self._validate_ux_code(ux_code)
            
            logger.info(f"✅ 表盘代码生成成功")
            logger.info(f"   代码长度: {len(ux_code)}")
            logger.info(f"   代码预览: {ux_code[:200]}...")
            
            return ux_code
            
        except Exception as e:
            logger.error(f"❌ 生成表盘代码失败: {str(e)}")
            logger.error(f"   错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"   堆栈: {traceback.format_exc()}")
            raise
    
    async def edit_watchface(
        self,
        current_code: str,
        instruction: str,
        assets: WatchfaceAssets
    ) -> str:
        """
        编辑现有表盘代码
        
        Args:
            current_code: 当前的index.ux代码
            instruction: 编辑指令
            assets: 可用素材
            
        Returns:
            修改后的index.ux代码
        """
        logger.info(f"✏️ 开始编辑vivo表盘代码")
        logger.info(f"   编辑指令: {instruction}")
        logger.info(f"   当前代码长度: {len(current_code)}")
        
        try:
            # 构建编辑提示词
            user_prompt = build_edit_prompt(current_code, instruction, assets)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 记录请求
            logger.info("📤 MiniMax API 编辑请求:")
            logger.info(f"   User Prompt长度: {len(user_prompt)}")
            
            # 调用MiniMax-M2
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.MAX_TOKENS,
                extra_body={"reasoning_split": True}
            )
            
            # 提取响应
            choice = response.choices[0]
            raw_content = choice.message.content
            
            # 提取reasoning
            reasoning_details = getattr(choice.message, 'reasoning_details', None)
            if reasoning_details:
                self.last_reasoning = " ".join([
                    detail.get('text', '') 
                    for detail in reasoning_details 
                    if isinstance(detail, dict)
                ])
            else:
                self.last_reasoning = "（无推理过程）"
            
            # 记录响应
            logger.info("📥 MiniMax API 编辑响应:")
            logger.info(f"   Reasoning: {self.last_reasoning[:300]}...")
            logger.info(f"   原始响应长度: {len(raw_content)}")
            
            # 提取新代码
            new_code = self._extract_ux_code(raw_content)
            
            # 验证代码
            self._validate_ux_code(new_code)
            
            # 计算diff
            diff = self._compute_diff(current_code, new_code)
            change_summary = self._generate_change_summary(diff)
            
            logger.info(f"✅ 表盘代码编辑成功")
            logger.info(f"   新代码长度: {len(new_code)}")
            logger.info(f"   变更摘要: {change_summary}")
            logger.info(f"   详细Diff:\n{chr(10).join(diff[:20])}")  # 只记录前20行
            
            return new_code
            
        except Exception as e:
            logger.error(f"❌ 编辑表盘代码失败: {str(e)}")
            logger.error(f"   错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"   堆栈: {traceback.format_exc()}")
            raise
    
    def _extract_ux_code(self, response: str) -> str:
        """从LLM响应中提取.ux代码"""
        logger.info("🔍 开始提取.ux代码")
        
        # 尝试多种匹配模式
        patterns = [
            r'```ux\n(.*?)\n```',
            r'```xml\n(.*?)\n```',
            r'```html\n(.*?)\n```',
            r'```\n(<template>.*?</style>)\n```',
            r'(<template>.*?</style>)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                code = match.group(1)
                # 验证代码包含必需的三个部分
                if '<template>' in code and '<script>' in code and '<style' in code:
                    logger.info(f"✅ 提取成功，使用模式: {pattern[:30]}...")
                    return code.strip()
        
        # 如果没有代码块标记，尝试直接提取
        if '<template>' in response and '</style>' in response:
            start = response.find('<template>')
            end = response.rfind('</style>') + len('</style>')
            code = response[start:end].strip()
            
            if '<script>' in code:
                logger.info("✅ 提取成功，直接匹配")
                return code
        
        # 提取失败
        logger.error("❌ 无法提取有效的.ux代码")
        logger.error(f"   响应内容: {response[:500]}...")
        raise ValueError("无法从响应中提取有效的.ux代码，请检查响应格式")
    
    def _validate_ux_code(self, code: str):
        """验证.ux代码的完整性"""
        logger.info("🔍 验证.ux代码")
        
        errors = []
        
        # 检查必需的标签
        if '<template>' not in code:
            errors.append("缺少<template>标签")
        if '</template>' not in code:
            errors.append("缺少</template>标签")
        if '<script>' not in code:
            errors.append("缺少<script>标签")
        if '</script>' not in code:
            errors.append("缺少</script>标签")
        if '<style' not in code:
            errors.append("缺少<style>标签")
        if '</style>' not in code:
            errors.append("缺少</style>标签")
        
        # 检查export default
        if 'export default' not in code:
            errors.append("script标签中缺少export default")
        
        # 检查基本结构
        if 'onInit' not in code:
            errors.append("缺少onInit生命周期函数")
        
        if errors:
            error_msg = "代码验证失败: " + ", ".join(errors)
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("✅ 代码验证通过")
    
    def _compute_diff(self, old_code: str, new_code: str) -> list:
        """计算代码差异"""
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='旧代码',
            tofile='新代码',
            lineterm=''
        ))
        
        return diff
    
    def _generate_change_summary(self, diff: list) -> str:
        """生成变更摘要"""
        added = len([line for line in diff if line.startswith('+')])
        removed = len([line for line in diff if line.startswith('-')])
        
        return f"新增{added}行，删除{removed}行"

