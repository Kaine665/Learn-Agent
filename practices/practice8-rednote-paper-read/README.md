# 实践8：小红书帖子阅读Agent

## 项目概述

这是一个小红书帖子阅读和管理Agent，帮助你：
- 📥 **获取帖子**：从小红书URL获取帖子内容
- 📝 **AI摘要**：自动生成帖子摘要和关键点
- 📚 **批量批阅**：快速批阅多个帖子
- 💬 **智能交互**：像管家一样陪你批阅文件
- 📊 **阅读统计**：跟踪阅读状态和进度

## 核心功能

### 1. 帖子获取
- **方式1：URL获取**（推荐）
  - 直接输入小红书帖子URL
  - 自动抓取标题、内容等信息
  
- **方式2：手动输入**（备用）
  - 如果URL获取失败，可以手动输入标题和内容
  - 适用于截图后手动输入的场景

### 2. AI摘要生成
- 自动生成帖子摘要（100-200字）
- 提取关键点
- 自动打标签

### 3. 批量批阅
- 一键批阅所有未读帖子
- 生成批阅报告
- 自动标记已读状态

### 4. 阅读管理
- 查看所有帖子列表
- 查看阅读状态（已读/未读）
- 添加批注和笔记

## 项目结构

```
practice8-rednote-paper-read/
├── models.py              # 数据模型（帖子、摘要、批注等）
├── storage.py             # 数据存储层（JSON文件）
├── tools.py               # 工具系统（网页抓取、OCR等）
├── rednote_core.py        # 核心业务逻辑（帖子获取、处理）
├── rednote_agent.py       # AI管家Agent（交互式批阅）
├── example.py             # 示例程序
└── README.md              # 说明文档
```

## 安装和使用

### 1. 安装依赖

```bash
pip install openai requests beautifulsoup4 python-dotenv
```

### 2. 配置API Key

**方式1：使用 .env 文件（推荐）**

在项目目录创建 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
```

**方式2：设置环境变量**

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
```

Linux/Mac:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### 3. 运行示例

```bash
python example.py
```

## 使用示例

### 示例1：添加帖子

```
💬 你：获取这个帖子：https://www.xiaohongshu.com/explore/xxxxx

🤖 管家：✅ 成功添加帖子！
📌 标题：xxx
👤 作者：xxx
🔗 链接：https://...
📝 内容预览：xxx...
```

### 示例2：总结未读帖子

```
💬 你：总结所有未读帖子

🤖 管家：📚 未读帖子摘要（共3篇）：
1. xxx
   摘要：xxx...
   链接：https://...
...
```

### 示例3：批量批阅

```
💬 你：批量批阅

🤖 管家：📋 批量批阅报告（共5篇）：
1. 【xxx】
   摘要：xxx...
   关键点：xxx, xxx, xxx
   链接：https://...
...
```

### 示例4：查看阅读状态

```
💬 你：阅读状态

🤖 管家：📊 阅读统计：
总帖子数：10
已读：7
未读：3
...
```

## 技术栈

- **LLM**: OpenAI GPT-4o-mini（用于摘要生成和对话）
- **网页抓取**: requests + BeautifulSoup（简单易用）
- **存储**: JSON文件（无需数据库）
- **OCR**: 预留接口（可选，需要时可添加PaddleOCR等）

## 设计特点

✅ **简单易用**：使用简单的技术栈，学习成本低  
✅ **模块化设计**：核心逻辑与UI分离，易于扩展  
✅ **智能交互**：AI管家理解自然语言，友好对话  
✅ **数据持久化**：所有数据保存在JSON文件中  

## 注意事项

1. **小红书URL获取**：
   - 目前使用简单的网页抓取，可能无法获取完整内容
   - 如果小红书有反爬虫机制，可能需要：
     - 使用小红书开放平台API（需要申请）
     - 使用截图+OCR的方式（需要手动操作）

2. **OCR功能**：
   - 当前版本未实现OCR功能
   - 如果需要，可以添加PaddleOCR或Tesseract
   - 也可以使用在线OCR API（如百度OCR、腾讯OCR）

3. **API限制**：
   - OpenAI API有调用限制和费用
   - 建议使用GPT-4o-mini（成本较低）

## 扩展建议

1. **添加OCR功能**：
   - 集成PaddleOCR用于图片文字识别
   - 支持截图后自动识别

2. **添加Web UI**：
   - 使用Streamlit创建Web界面
   - 更友好的交互体验

3. **添加小红书API**：
   - 申请小红书开放平台API
   - 获取更完整的帖子信息

4. **添加视频处理**：
   - 提取视频字幕
   - 分析视频内容

## 常见问题

**Q: 为什么无法获取小红书帖子内容？**  
A: 小红书可能有反爬虫机制。可以尝试：
- 手动输入帖子内容（使用"手动输入"功能）
- 截图后使用OCR（需要添加OCR功能）
- 申请小红书开放平台API

**Q: 如何添加OCR功能？**  
A: 可以安装PaddleOCR：
```bash
pip install paddlepaddle paddleocr
```
然后在 `tools.py` 中实现OCR功能。

**Q: 数据存储在哪里？**  
A: 所有数据保存在 `data/` 目录下的JSON文件中：
- `posts.json`: 帖子列表
- `summaries.json`: 摘要数据
- `notes.json`: 批注数据
- `reading_status.json`: 阅读状态

## 许可证

本项目仅供学习使用。

