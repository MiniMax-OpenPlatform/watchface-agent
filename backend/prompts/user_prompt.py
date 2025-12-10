"""
用户提示词构建 - 生成标准 HTML 表盘
"""

from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.assets import WatchfaceAssets, AssetFile
from models.project import WatchfaceConfig


def build_generation_prompt(
    instruction: str,
    assets: WatchfaceAssets,
    config: WatchfaceConfig
) -> str:
    """构建生成提示词"""
    
    # 素材清单
    assets_list = []
    
    # 背景素材
    if assets.background_round:
        assets_list.append(f"- 背景图: {assets.background_round.stored_filename}")
    if assets.background_square:
        assets_list.append(f"- 备用背景: {assets.background_square.stored_filename}")
    
    # 指针素材
    if assets.pointer_hour:
        assets_list.append(f"- 时针图片: {assets.pointer_hour.stored_filename}")
    if assets.pointer_minute:
        assets_list.append(f"- 分针图片: {assets.pointer_minute.stored_filename}")
    if assets.pointer_second:
        assets_list.append(f"- 秒针图片: {assets.pointer_second.stored_filename}")
    
    # 数字素材
    if assets.digits:
        digit_files = [f.stored_filename for f in assets.digits]
        assets_list.append(f"- 数字图片(0-9): {', '.join(digit_files)}")
    
    # 星期素材
    if assets.week_images:
        week_files = [f.stored_filename for f in assets.week_images]
        assets_list.append(f"- 星期图片(1-7): {', '.join(week_files)}")
    
    # 装饰素材
    if assets.decorations:
        deco_files = [f.stored_filename for f in assets.decorations]
        assets_list.append(f"- 装饰元素: {', '.join(deco_files)}")
    
    # 判断是否有素材
    has_assets = len(assets_list) > 0
    
    if has_assets:
        # 构建更详细的素材使用说明
        usage_instructions = []
        if assets.background_round:
            usage_instructions.append(f"✓ 表盘背景必须使用: background-image: url('./assets/{assets.background_round.stored_filename}');")
        if assets.background_square:
            usage_instructions.append(f"✓ 备用背景可用: background-image: url('./assets/{assets.background_square.stored_filename}');")
        if assets.pointer_hour:
            usage_instructions.append(f"✓ 时针必须使用: <img src='./assets/{assets.pointer_hour.stored_filename}' />")
        if assets.pointer_minute:
            usage_instructions.append(f"✓ 分针必须使用: <img src='./assets/{assets.pointer_minute.stored_filename}' />")
        if assets.pointer_second:
            usage_instructions.append(f"✓ 秒针必须使用: <img src='./assets/{assets.pointer_second.stored_filename}' />")
        
        prompt = f"""用户需求：
{instruction}

🎨 已上传素材清单：
{chr(10).join(assets_list)}

⚠️ 素材使用要求（必须严格执行）：
{chr(10).join(usage_instructions) if usage_instructions else ''}

🚨 代码生成前检查清单：
1. 如果有背景图，代码中必须包含 background-image: url('./assets/xxx')
2. 不允许使用渐变色（linear-gradient）或纯色替代背景图
3. 如果是指针表盘，数字位置必须正确：12在上、3在右、6在下、9在左
4. 使用三角函数计算数字位置，不要随意摆放
5. 所有指针的旋转中心必须在表盘正中心

请生成一个完整的HTML表盘文件，可以直接在浏览器中运行。
"""
    else:
        prompt = f"""用户需求：
{instruction}

可用素材：
（无素材，请用纯代码实现）

请生成一个完整的HTML表盘文件，可以直接在浏览器中运行。
- 请根据用户需求智能决定表盘样式（指针/数字/混合）
- 请根据用户需求决定是否显示日期、星期等元素
- 发挥创意，实现符合用户期望的表盘效果
"""
    
    return prompt


def build_edit_prompt(
    current_code: str,
    instruction: str,
    assets: WatchfaceAssets
) -> str:
    """构建编辑提示词"""
    
    # 收集可用素材（详细说明）
    available_assets = []
    usage_instructions = []
    
    # 背景素材
    if assets.background_round:
        available_assets.append(f"- 圆形背景图: {assets.background_round.stored_filename}")
        usage_instructions.append(f"✓ 圆形背景: background-image: url('./assets/{assets.background_round.stored_filename}');")
    if assets.background_square:
        available_assets.append(f"- 方形背景图: {assets.background_square.stored_filename}")
        usage_instructions.append(f"✓ 方形背景: background-image: url('./assets/{assets.background_square.stored_filename}');")
    
    # 指针素材（关键：明确说明用户说"指针"/"秒针"等时应该用哪个）
    if assets.pointer_hour:
        available_assets.append(f"- 时针图片: {assets.pointer_hour.stored_filename}")
        usage_instructions.append(f"✓ 时针: <img src='./assets/{assets.pointer_hour.stored_filename}' class='hour-hand' />")
    if assets.pointer_minute:
        available_assets.append(f"- 分针图片: {assets.pointer_minute.stored_filename}")
        usage_instructions.append(f"✓ 分针: <img src='./assets/{assets.pointer_minute.stored_filename}' class='minute-hand' />")
    if assets.pointer_second:
        available_assets.append(f"- 秒针图片: {assets.pointer_second.stored_filename}")
        usage_instructions.append(f"✓ 秒针: <img src='./assets/{assets.pointer_second.stored_filename}' class='second-hand' />")
    
    # 数字素材
    if assets.digits:
        digit_files = [f.stored_filename for f in assets.digits]
        available_assets.append(f"- 数字图片(0-9): {', '.join(digit_files)}")
        usage_instructions.append(f"✓ 数字显示: 使用 <img src='./assets/digit_X.png' /> 其中X为0-9")
    
    # 星期素材
    if assets.week_images:
        week_files = [f.stored_filename for f in assets.week_images]
        available_assets.append(f"- 星期图片(1-7): {', '.join(week_files)}")
        usage_instructions.append(f"✓ 星期显示: 使用 <img src='./assets/week_X.png' /> 其中X为1-7（周一到周日）")
    
    # 装饰素材
    if assets.decorations:
        deco_files = [f.stored_filename for f in assets.decorations]
        available_assets.append(f"- 装饰元素: {', '.join(deco_files)}")
    
    has_assets = len(available_assets) > 0
    
    if has_assets:
        prompt = f"""当前表盘代码：
```html
{current_code}
```

用户修改要求：
{instruction}

🎨 已上传素材清单：
{chr(10).join(available_assets)}

📝 素材使用方法（直接参考）：
{chr(10).join(usage_instructions) if usage_instructions else ''}

⚠️ 智能理解规则：
1. 当用户说"秒针"、"秒针图片"、"我上传的秒针"时，应该使用上面列出的"秒针图片"素材
2. 当用户说"时针"、"分针"时，同理使用对应的素材
3. 当用户说"背景"、"背景图"时，使用上传的背景图素材
4. 当用户说"数字"时，使用上传的数字图片素材
5. 素材路径格式: './assets/文件名'
6. 不要询问用户文件名，直接使用上面列出的素材！

🚨 最小化修改原则（极其重要）：
1. **只修改用户明确要求修改的部分**
2. **保持代码的整体结构、样式、布局完全不变**
3. 例如：用户说"秒针替换成图片" → 只找到秒针元素，改成 <img src='./assets/xxx' />，其他一切保持原样
4. **不要重新设计、不要"优化"、不要改变风格**

请返回完整的修改后 HTML 代码。
"""
    else:
        prompt = f"""当前表盘代码：
```html
{current_code}
```

用户修改要求：
{instruction}

可用素材：
（无额外素材）

请根据用户要求修改代码，返回完整的修改后 HTML 代码。
"""
    
    return prompt
