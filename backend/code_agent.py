"""
WatchFace Code Agent - Core Implementation
真正的Coding Agent，支持完整代码生成和智能代码编辑
"""
from openai import OpenAI
import difflib
import re
from datetime import datetime
from typing import Dict, List, Optional
from config import settings
from logging_config import get_logger
from prompts.system_prompt import WATCHFACE_SYSTEM_PROMPT
from prompts.user_prompt import build_generation_prompt, build_edit_prompt

# Initialize logger
logger = get_logger()


class WatchFaceCodeAgent:
    """手表表盘Code Agent - 真正的代码生成和编辑"""
    
    def __init__(self, api_key: Optional[str] = None, client_id: Optional[str] = None):
        """
        初始化Code Agent
        
        Args:
            api_key: 可选的API Key（如果提供则使用，否则使用默认配置）
            client_id: 客户端ID（用于日志记录）
        """
        # 使用提供的API Key或默认配置
        actual_api_key = api_key or settings.minimax_api_key
        
        if not actual_api_key:
            raise ValueError("No API Key provided and MINIMAX_API_KEY not configured")
        
        # 配置MiniMax-M2客户端（设置较长的超时时间）
        self.llm = OpenAI(
            base_url=settings.minimax_base_url,
            api_key=actual_api_key,
            timeout=180.0  # 3分钟超时 - AI代码生成可能需要较长时间
        )
        
        self.model = settings.minimax_model
        self.temperature = settings.default_temperature
        self.max_tokens = settings.max_tokens
        self.enable_reasoning = settings.enable_reasoning
        self.client_id = client_id
        
        key_source = f"客户端 {client_id[:16] if client_id else 'default'}..." if api_key else "默认配置"
        print(f"✅ Code Agent initialized with {self.model} (Key来源: {key_source})")
    
    async def process_instruction(
        self, 
        user_input: str, 
        current_code: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        assets = None,
        config = None
    ) -> Dict:
        """
        处理用户指令 - Code Agent核心流程
        
        Args:
            user_input: 用户指令
            current_code: 当前代码（如果是修改场景）
            conversation_history: 对话历史
            assets: 素材信息
            config: 配置信息
        
        Returns:
            包含code、diff、reasoning等信息的字典
        """
        is_new_conversation = current_code is None
        
        # 🔍 日志：记录process_instruction入口
        entry_log = f"""
{"="*70}
🤖 Code Agent 处理开始
{"="*70}
场景类型: {'新建表盘 (完整生成)' if is_new_conversation else '修改表盘 (智能编辑)'}
用户指令: {user_input}
当前代码: {'无 (新建)' if is_new_conversation else f'{len(current_code)} 字符'}
对话历史: {len(conversation_history) if conversation_history else 0} 轮
时间戳: {datetime.now().isoformat()}
{"="*70}
"""
        print(entry_log)
        logger.info(entry_log)
        
        try:
            if is_new_conversation:
                # 场景1：从零生成完整代码
                result = await self.generate_complete_code(user_input, assets, config)
            else:
                # 场景2：智能代码编辑
                result = await self.edit_code(
                    user_input, 
                    current_code, 
                    conversation_history or [],
                    assets,
                    config
                )
            
            # 🔍 日志：记录process_instruction结果汇总
            summary_log = f"""
{"="*70}
✅ Code Agent 处理完成
{"="*70}
成功状态: {result.get('success')}
返回消息: {result.get('message')}
代码长度: {len(result.get('code', '')) if result.get('code') else 0} 字符
包含思考: {bool(result.get('reasoning'))}
包含差异: {bool(result.get('diff'))}
处理时间: {datetime.now().isoformat()}
{"="*70}
"""
            print(summary_log)
            logger.info(summary_log)
            
            return result
            
        except Exception as e:
            # 🔍 日志：记录process_instruction异常
            exception_log = f"""
{"="*70}
❌ Code Agent 处理异常
{"="*70}
异常类型: {type(e).__name__}
异常消息: {str(e)}
用户指令: {user_input}
场景类型: {'新建表盘' if is_new_conversation else '修改表盘'}
{"="*70}
"""
            print(exception_log)
            logger.error(exception_log, exc_info=True)
            raise
    
    async def generate_complete_code(self, user_input: str, assets=None, config=None) -> Dict:
        """
        场景1：从零生成完整表盘代码
        
        这是真正的Code Agent能力 - 不使用模板，从零创作
        """
        print("🎨 Generating complete watchface code from scratch...")
        
        # 使用导入的系统提示词
        system_prompt = WATCHFACE_SYSTEM_PROMPT
        
        # 使用提示词构建函数生成用户消息
        if assets and config:
            user_message = build_generation_prompt(user_input, assets, config)
            logger.info(f"✓ 使用素材信息构建提示词")
        else:
            # 如果没有提供assets和config，使用简化版本
            user_message = f"""请为我创建一个表盘：

{user_input}

直接生成完整的HTML代码，让我能在浏览器中看到效果。"""
            logger.warning("⚠️ 未提供素材和配置信息，使用简化提示词")

        try:
            # 调用MiniMax-M2生成代码
            extra_body = {}
            if self.enable_reasoning:
                extra_body["reasoning_split"] = True
            
            # 准备请求参数
            request_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # 🔍 日志：记录发送给MiniMax的请求（同时写入文件和终端）
            log_msg = "\n" + "="*70 + "\n📤 MiniMax API 请求详情\n" + "="*70
            print(log_msg)
            logger.info(log_msg)
            
            request_info = f"""模型: {self.model}
Temperature: {self.temperature}
Max Tokens: {self.max_tokens}
启用Reasoning: {self.enable_reasoning}

--- System Prompt (前200字符) ---
{system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt}

--- User Message (前200字符) ---
{user_message[:200] + "..." if len(user_message) > 200 else user_message}"""
            
            print(request_info)
            logger.info(request_info)
            print("="*70 + "\n")
            logger.info("="*70)
            
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=request_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                extra_body=extra_body
            )
            
            # 🔍 日志：记录MiniMax的原始响应（同时写入文件和终端）
            raw_content = response.choices[0].message.content
            
            # 打印完整的Text内容（用户需求）
            print("\n" + "="*70)
            print(f"📄 Agent返回的完整原始内容 (Text):")
            print("="*70)
            print(raw_content)
            print("="*70 + "\n")
            
            response_log = f"""
{"="*70}
📥 MiniMax API 响应详情
{"="*70}
Response ID: {response.id if hasattr(response, 'id') else 'N/A'}
Model: {response.model if hasattr(response, 'model') else 'N/A'}
Finish Reason: {response.choices[0].finish_reason if response.choices else 'N/A'}

--- 原始内容 (前500字符) ---
{raw_content[:500] + "..." if len(raw_content) > 500 else raw_content}

--- 原始内容统计 ---
总长度: {len(raw_content)} 字符
总行数: {len(raw_content.split(chr(10)))} 行"""
            
            print(response_log)
            logger.info(response_log)
            
            # 提取生成的代码
            code = self._extract_code_from_response(raw_content)
            
            # 🔍 日志：记录提取后的代码
            code_log = f"""
--- 提取的代码 (前500字符) ---
{code[:500] + "..." if len(code) > 500 else code}

--- 提取后代码统计 ---
代码长度: {len(code)} 字符
代码行数: {len(code.split(chr(10)))} 行"""
            
            print(code_log)
            logger.info(code_log)
            
            # 获取Agent思考过程
            reasoning = ""
            if self.enable_reasoning and hasattr(response.choices[0].message, 'reasoning_details'):
                if response.choices[0].message.reasoning_details:
                    reasoning = response.choices[0].message.reasoning_details[0].get('text', '')
                    
                    reasoning_log = f"""
--- Agent思考过程 (前300字符) ---
{reasoning[:300] + "..." if len(reasoning) > 300 else reasoning}
思考过程总长度: {len(reasoning)} 字符"""
                    
                    print(reasoning_log)
                    logger.info(reasoning_log)
            
            # 🔍 日志：记录最终生成结果
            newline = '\n'
            final_result_log = f"""
✅ 代码生成完成
---
成功: True
代码行数: {len(code.split(newline))}
代码字符数: {len(code)}
包含思考过程: {bool(reasoning)}
思考过程长度: {len(reasoning) if reasoning else 0} 字符
{"="*70}
"""
            print(final_result_log)
            logger.info(final_result_log)
            
            return {
                "success": True,
                "code": code,
                "reasoning": reasoning,
                "raw_content": raw_content,  # 🆕 保存完整的原始content
                "message": "✅ 完整表盘代码生成成功！",
                "diff": None,  # 新建无diff
                "stats": {
                    "lines": len(code.split('\n')),
                    "characters": len(code)
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # 友好的错误提示
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                user_message = "⏱️ 请求超时：AI模型响应时间较长，请尝试简化指令或稍后重试"
            elif "connection" in error_msg.lower():
                user_message = "🔌 连接错误：无法连接到AI模型服务，请检查网络和API配置"
            elif "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                user_message = "🔑 认证错误：API密钥无效或已过期"
            else:
                user_message = f"❌ 代码生成失败: {error_msg}"
            
            # 🔍 日志：记录详细错误信息
            error_log = f"""
{"="*70}
❌ 代码生成失败
{"="*70}
错误类型: {type(e).__name__}
错误消息: {error_msg}
用户友好提示: {user_message}
指令: {user_input}
{"="*70}
"""
            print(error_log)
            logger.error(error_log, exc_info=True)  # 包含完整堆栈跟踪
            
            return {
                "success": False,
                "code": None,
                "reasoning": None,
                "message": user_message,
                "error": error_msg
            }
    
    async def edit_code(
        self, 
        user_input: str, 
        current_code: str,
        conversation_history: List[Dict],
        assets=None,
        config=None
    ) -> Dict:
        """
        场景2：智能代码编辑
        
        Code Agent的关键能力 - 理解用户意图并智能修改代码
        """
        print("✏️  Editing code intelligently...")
        
        # 使用导入的系统提示词（包含素材使用规则）
        system_prompt = WATCHFACE_SYSTEM_PROMPT + """

## 🔧 代码编辑特殊要求

### 1. 最小化修改原则 🚨（最重要）

**核心规则：只改用户要求的部分，保持其他部分完全不变！**

- ✅ 用户说"秒针替换成图片" → 只修改秒针相关代码（找到秒针元素，替换为<img>）
- ✅ 用户说"背景改成蓝色" → 只修改background属性
- ✅ 用户说"添加日期显示" → 只添加日期元素，其他不变
- ❌ 不要重新设计整个表盘！
- ❌ 不要改变原有的布局、颜色、字体等！
- ❌ 不要"顺便优化"其他部分！

**修改步骤：**
1. 仔细分析当前代码，找到需要修改的具体部分
2. 只修改那一小部分代码
3. 确保修改后的代码与原代码风格一致
4. 保持HTML结构、CSS样式、JavaScript逻辑的其他部分完全不变

### 2. 智能素材匹配 ⚠️（最重要）

当用户提到素材时，你必须**智能推断**他们指的是哪个素材，**不要询问文件名**！

**推断规则：**
- 用户说"秒针" / "秒针图片" / "我的秒针" / "上传的秒针" 
  → 查找素材清单中的"秒针图片: xxx.png"，直接使用！
  
- 用户说"时针" / "时针图片"
  → 查找素材清单中的"时针图片: xxx.png"，直接使用！
  
- 用户说"分针" / "分针图片"
  → 查找素材清单中的"分针图片: xxx.png"，直接使用！
  
- 用户说"背景" / "背景图" / "我上传的背景"
  → 查找素材清单中的"背景图: xxx.png"，直接使用！
  
- 用户说"指针图片"（没说具体是哪根）
  → 根据上下文判断，可能是时针、分针或秒针

**禁止行为：**
❌ 不要回复："请提供文件名"
❌ 不要说："我需要知道具体的文件名"
❌ 不要要求用户提供更多信息

**正确做法：**
✅ 直接查看素材清单
✅ 找到对应的素材文件名
✅ 在代码中使用该文件名

### 3. 意图理解示例
- "把背景改成蓝色" → 只改背景颜色相关代码
- "使用我上传的背景图" → 从素材清单找到背景图，用 background-image: url('./assets/xxx')
- "秒针替换成我上传的指针图片" → 从素材清单找到秒针图片，替换为 <img src='./assets/xxx' />
- "加个日期显示在右边" → 添加日期元素和相关逻辑
- "指针太粗了" → 调整指针的宽度样式

### 4. 输出要求
返回修改后的完整HTML代码。
保持代码风格一致，确保可以正常运行。"""

        # 使用提示词构建函数
        if assets:
            base_message = build_edit_prompt(current_code, user_input, assets)
        else:
            # 简化版本
            base_message = f"""当前表盘代码：
```html
{current_code}
```

用户修改要求：
{user_input}

请根据用户要求修改代码，返回完整的修改后 HTML 代码。"""
        
        # 添加对话上下文
        context_summary = ""
        if conversation_history:
            recent = conversation_history[-3:]  # 最近3轮更聚焦
            context_summary = "\n\n### 对话历史：\n"
            for msg in recent:
                role = "👤 用户" if msg.get('role') == 'user' else "🤖 助手"
                content = msg.get('content', '')[:200]
                context_summary += f"{role}: {content}\n"
        
        user_message = base_message + context_summary

        try:
            extra_body = {}
            if self.enable_reasoning:
                extra_body["reasoning_split"] = True
            
            request_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # 🔍 日志：记录编辑请求（同时写入文件和终端）
            request_log = f"""
{"="*70}
📤 MiniMax API 编辑请求详情
{"="*70}
模型: {self.model}
场景: 代码编辑
用户指令: {user_input}
当前代码长度: {len(current_code)} 字符
对话历史: {len(conversation_history) if conversation_history else 0} 轮
{"="*70}"""
            
            print(request_log)
            logger.info(request_log)
            
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=request_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                extra_body=extra_body
            )
            
            # 🔍 日志：记录编辑响应（同时写入文件和终端）
            raw_content = response.choices[0].message.content
            
            # 打印完整的Text内容（用户需求）
            print("\n" + "="*70)
            print(f"📄 Agent返回的完整原始内容 (Text) - 编辑模式:")
            print("="*70)
            print(raw_content)
            print("="*70 + "\n")
            
            edit_response_log = f"""
{"="*70}
📥 MiniMax API 编辑响应详情
{"="*70}
Response ID: {response.id if hasattr(response, 'id') else 'N/A'}
原始响应长度: {len(raw_content)} 字符

--- 原始响应内容 (前500字符) ---
{raw_content[:500] + "..." if len(raw_content) > 500 else raw_content}"""
            
            print(edit_response_log)
            logger.info(edit_response_log)
            
            # 提取修改后的代码
            new_code = self._extract_code_from_response(raw_content)
            
            extracted_log = f"""
--- 提取后的新代码 (前500字符) ---
{new_code[:500] + "..." if len(new_code) > 500 else new_code}
新代码长度: {len(new_code)} 字符"""
            
            print(extracted_log)
            logger.info(extracted_log)
            
            # 获取思考过程
            reasoning = ""
            if self.enable_reasoning and hasattr(response.choices[0].message, 'reasoning_details'):
                if response.choices[0].message.reasoning_details:
                    reasoning = response.choices[0].message.reasoning_details[0].get('text', '')
                    
                    thinking_log = f"""
--- Agent思考过程 (前300字符) ---
{reasoning[:300] + "..." if len(reasoning) > 300 else reasoning}"""
                    
                    print(thinking_log)
                    logger.info(thinking_log)
                    print(f"💭 Agent Thinking: {reasoning[:200]}...")
            
            # 计算代码差异
            diff = self._compute_diff(current_code, new_code)
            
            # 🔍 日志：记录代码差异（同时写入文件和终端）
            diff_log = f"""
--- 代码差异分析 ---
新增行数: {len(diff['added_lines'])}
删除行数: {len(diff['removed_lines'])}
总变更数: {diff['total_changes']}"""
            
            if diff['added_lines']:
                diff_log += "\n\n新增的行（前5行）:"
                for line in diff['added_lines'][:5]:
                    diff_log += f"\n  + 第{line['line_number']}行: {line['content'][:60]}"
            
            if diff['removed_lines']:
                diff_log += "\n\n删除的行（前5行）:"
                for line in diff['removed_lines'][:5]:
                    diff_log += f"\n  - 第{line['line_number']}行: {line['content'][:60]}"
            
            # 生成友好的修改说明
            change_summary = self._generate_change_summary(diff)
            
            diff_log += f"\n\n修改摘要: {change_summary}\n{'='*70}\n"
            
            print(diff_log)
            logger.info(diff_log)
            
            # 🔍 日志：记录最终编辑结果
            newline = '\n'
            final_edit_log = f"""
✅ 代码编辑完成
---
成功: True
新代码行数: {len(new_code.split(newline))}
新代码字符数: {len(new_code)}
总变更数: {diff['total_changes']}
新增行数: {len(diff['added_lines'])}
删除行数: {len(diff['removed_lines'])}
包含思考过程: {bool(reasoning)}
修改摘要: {change_summary}
{"="*70}
"""
            print(final_edit_log)
            logger.info(final_edit_log)
            
            return {
                "success": True,
                "code": new_code,
                "reasoning": reasoning,
                "raw_content": raw_content,  # 🆕 保存完整的原始content
                "diff": diff,
                "message": f"✅ 代码修改完成！{change_summary}",
                "stats": {
                    "lines": len(new_code.split(newline)),
                    "changes": diff['total_changes']
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # 🔍 日志：记录详细错误信息
            error_log = f"""
{"="*70}
❌ 代码编辑失败
{"="*70}
错误类型: {type(e).__name__}
错误消息: {error_msg}
用户指令: {user_input}
当前代码长度: {len(current_code)} 字符
{"="*70}
"""
            print(error_log)
            logger.error(error_log, exc_info=True)  # 包含完整堆栈跟踪
            
            return {
                "success": False,
                "code": current_code,  # 失败时返回原代码
                "reasoning": None,
                "diff": None,
                "message": f"❌ 代码修改失败: {error_msg}",
                "error": error_msg
            }
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """从LLM响应中提取代码"""
        # 处理markdown代码块
        if "```html" in response_text:
            start = response_text.find("```html") + 7
            end = response_text.find("```", start)
            if end != -1:
                return response_text[start:end].strip()
        
        if "```" in response_text:
            start = response_text.find("```") + 3
            # 跳过可能的语言标识符
            if response_text[start:start+10].strip().split()[0] in ['html', 'xml']:
                start = response_text.find('\n', start) + 1
            end = response_text.find("```", start)
            if end != -1:
                return response_text[start:end].strip()
        
        # 尝试找到<!DOCTYPE html>
        if "<!DOCTYPE html>" in response_text or "<html>" in response_text:
            start = response_text.find("<!DOCTYPE html>")
            if start == -1:
                start = response_text.find("<html>")
            if start != -1:
                # 找到</html>结束
                end = response_text.rfind("</html>")
                if end != -1:
                    return response_text[start:end+7].strip()
        
        # 如果都没找到，返回全部内容
        return response_text.strip()
    
    def _compute_diff(self, old_code: str, new_code: str) -> Dict:
        """计算代码差异"""
        old_lines = old_code.split('\n')
        new_lines = new_code.split('\n')
        
        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))
        
        changes = {
            "added_lines": [],
            "removed_lines": [],
            "modified_sections": [],
            "total_changes": 0
        }
        
        line_num = 0
        for line in diff:
            if line.startswith('+ '):
                changes["added_lines"].append({
                    "line_number": line_num,
                    "content": line[2:]
                })
                changes["total_changes"] += 1
                line_num += 1
            elif line.startswith('- '):
                changes["removed_lines"].append({
                    "line_number": line_num,
                    "content": line[2:]
                })
                changes["total_changes"] += 1
            elif line.startswith('  '):
                line_num += 1
        
        return changes
    
    def _generate_change_summary(self, diff: Dict) -> str:
        """生成易读的修改摘要"""
        added = len(diff.get('added_lines', []))
        removed = len(diff.get('removed_lines', []))
        
        if added > 0 and removed > 0:
            return f"修改了 {added} 行，删除了 {removed} 行"
        elif added > 0:
            return f"新增了 {added} 行代码"
        elif removed > 0:
            return f"删除了 {removed} 行代码"
        else:
            return "代码已优化"


# 全局Code Agent实例
_code_agent_instance = None

def get_code_agent() -> WatchFaceCodeAgent:
    """获取Code Agent单例"""
    global _code_agent_instance
    if _code_agent_instance is None:
        _code_agent_instance = WatchFaceCodeAgent()
    return _code_agent_instance

