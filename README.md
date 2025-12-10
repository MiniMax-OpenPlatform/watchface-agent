# 🎨 WatchFace Agent

基于MiniMax-M2的智能手表表盘设计平台，通过对话即可创建专业级手表表盘UI。

## ✨ 核心特点

**对话即创作**  
用自然语言描述想法，AI自动生成完整的表盘代码
```
"创建一个运动风格的表盘，深色背景，显示步数和心率"
→ 30秒后得到可运行的完整代码
```

**智能迭代优化**  
通过多轮对话持续完善设计，无需重新开始
```
"把步数改成圆形进度条" → 精准修改，其他部分保持不变
"心率数字放大一些" → 立即生效
```

**代码完全透明**  
所有生成的代码都可查看和手动编辑，AI与人工无缝协作

**实时预览**  
Web端即时渲染，秒级查看设计效果

## 🤖 为什么选择MiniMax-M2？

WatchFace Agent采用**Code Agent架构**，不是简单的参数配置工具，而是真正理解代码、能够智能生成和编辑的AI智能体。

**MiniMax-M2的三大优势：**

1. **Interleaved Thinking（交织思考）**  
   在生成代码时展现思考过程，确保代码质量和可靠性

2. **深度代码理解**  
   精准理解HTML、SVG、JavaScript，能够准确定位需要修改的代码片段

3. **超强中文能力**  
   深度理解中文设计需求，适配国内手表厂商的使用习惯

## 🚀 快速开始

### 1. Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/MiniMax-OpenPlatform/watchface-agent.git
cd watchface-agent

# 设置API密钥
export MINIMAX_API_KEY=your_api_key_here

# 启动服务
docker-compose up -d

# 访问
open http://localhost:5173
```

### 2. 本地开发

**后端启动：**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**前端启动：**
```bash
cd frontend
npm install
npm run dev
```

### 3. 获取API密钥

访问 [MiniMax开放平台](https://platform.minimaxi.com/) 注册并获取API密钥

## 💡 使用示例

### 创建运动表盘
```
👤 "创建一个运动风格的表盘，深蓝色背景，显示时间、步数和心率"

🤖 [生成完整代码...]
   • 深蓝色渐变背景
   • 白色粗体指针
   • 环形步数进度条
   • 心率实时显示

✅ 30秒完成
```

### 快速修改
```
👤 "把步数进度条改成橙色，放大50%"

🤖 [智能定位并修改...]
   • 精准修改进度条颜色和大小
   • 其他元素保持不变

✅ 10秒完成
```

### 添加功能
```
👤 "增加一个显示天气的小组件"

🤖 [生成并插入新组件...]
   • 天气图标SVG
   • 温度数字显示
   • 自动布局调整

✅ 20秒完成
```

## 📈 效率对比

| 任务 | 传统开发 | WatchFace Agent | 提升 |
|-----|---------|-----------------|------|
| 创建新表盘 | 30分钟 | 30秒 | **60倍** |
| 修改样式 | 10分钟 | 10秒 | **60倍** |
| 添加功能 | 1小时 | 1分钟 | **60倍** |

## 🏢 应用场景

### 手机厂商快速开发
- **华为/荣耀**：快速推出运动健康主题表盘系列
- **小米/Redmi**：每月产出20-30款潮流个性化表盘
- **OPPO/vivo**：高效创建轻奢商务风格表盘
- **新品牌**：快速模仿学习Apple Watch经典设计

### 设计师原型探索
通过对话快速生成多个设计方案，加速创意验证

### 开发者效率工具
AI生成框架代码，开发者专注于细节优化和性能调优

## 🛠️ 技术架构

**前端：** React 18 + TypeScript + TailwindCSS + Monaco Editor  
**后端：** Python FastAPI + WebSocket  
**AI模型：** MiniMax-M2 (OpenAI兼容接口)  
**部署：** Docker + Docker Compose

## 📖 核心概念

### Code Agent vs 参数配置

传统工具：提取参数 → 填充模板 → 有限选择  
WatchFace Agent：理解需求 → 生成代码 → 无限创造

**关键区别：**
- ❌ 不是从模板中选择
- ✅ 而是从零开始创作
- ❌ 不是修改配置参数
- ✅ 而是智能编辑代码

## 🤝 参与贡献

欢迎提交Issue和Pull Request！

```bash
git checkout -b feature/YourFeature
git commit -m 'Add some feature'
git push origin feature/YourFeature
```

## 📄 开源协议

MIT License

## 🔗 相关链接

- [MiniMax开放平台](https://platform.minimaxi.com/)
- [MiniMax-M2 API文档](https://platform.minimaxi.com/docs/api-reference/text-openai-api)
- [技术支持](mailto:Model@minimaxi.com)

---

**让任何人都能通过对话创造专业级手表表盘！** 🚀

通过MiniMax-M2的强大能力，WatchFace Agent重新定义了表盘设计的方式。
