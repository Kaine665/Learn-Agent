## 📰 ➡️ 🎙️ Blog to Podcast Agent

将博客文章转换为播客音频的工具。使用 OpenAI GPT-4 生成摘要，Firecrawl 抓取博客内容，ElevenLabs API 生成音频。

## 架构设计

项目采用**分层架构**，将业务逻辑与 UI 分离：

- **`blog_to_podcast_core.py`**: 核心业务逻辑模块（**不依赖任何 UI 框架**）
  - `BlogToPodcastConverter` 类：提供完整的转换功能
  - 可以独立使用，也可以被其他 UI 框架调用

- **`blog_to_podcast_agent.py`**: Streamlit Web UI（依赖 Streamlit）
  - 基于核心模块构建的 Web 界面
  - 适合交互式使用

- **`blog_to_podcast_cli.py`**: 命令行工具（不依赖 Streamlit）
  - 基于核心模块构建的 CLI 版本
  - 适合脚本化和自动化场景

## Features

- **Blog Scraping**: 使用 Firecrawl API 抓取任何公开博客 URL 的完整内容

- **Summary Generation**: 使用 OpenAI GPT-4 生成简洁、引人入胜的摘要（最多 2000 字符）

- **Podcast Generation**: 使用 ElevenLabs 语音 API 将摘要转换为音频播客

- **灵活的架构**: 核心逻辑不依赖 UI，可以轻松集成到其他应用中

- **多种使用方式**: 支持 Web UI、CLI 命令行，或作为 Python 模块导入使用

## Setup

### Requirements 

1. **API Keys** (三种设置方式，任选其一):

    **方式一：使用 .env 文件（推荐）**
    - 在项目根目录创建 `.env` 文件
    - 添加以下内容：
      ```
      OPENAI_API_KEY=your_openai_api_key_here
      ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
      FIRECRAWL_API_KEY=your_firecrawl_api_key_here
      ```
    
    **方式二：设置环境变量**
    - Windows PowerShell:
      ```powershell
      $env:OPENAI_API_KEY="your_openai_api_key"
      $env:ELEVENLABS_API_KEY="your_elevenlabs_api_key"
      $env:FIRECRAWL_API_KEY="your_firecrawl_api_key"
      ```
    - Linux/Mac:
      ```bash
      export OPENAI_API_KEY="your_openai_api_key"
      export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
      export FIRECRAWL_API_KEY="your_firecrawl_api_key"
      ```
    
    **方式三：在 Streamlit 界面输入**
    - 运行应用后，在侧边栏的 API Keys 输入框中输入

    **API Keys 获取地址：**
    - **OpenAI API Key**: https://platform.openai.com/api-keys
    - **ElevenLabs API Key**: https://elevenlabs.io/app/settings/api-keys
    - **Firecrawl API Key**: https://firecrawl.dev

2. **Python 3.8+**: Ensure you have Python 3.8 or higher installed.

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps
   cd ai_agent_tutorials/ai_blog_to_podcast_agent
   ```

2. Install the required Python packages:

   **Windows 用户注意**: 由于 Windows 路径长度限制，`elevenlabs` 包可能无法安装到虚拟环境中。推荐使用 `--user` 安装：
   ```bash
   # 推荐方式：安装到用户目录（避免路径长度问题）
   pip install --user -r requirements.txt
   
   # 或者直接安装到当前 Python 环境
   pip install -r requirements.txt
   ```
   
   如果遇到路径长度错误，请使用 `pip install --user` 方式安装。

## 使用方式

### 方式一：Streamlit Web UI（交互式）

1. 启动 Streamlit 应用：
   
   **重要**: 如果当前在虚拟环境中（提示符显示 `(.venv)`），请先退出虚拟环境：
   ```powershell
   deactivate
   ```
   
   然后运行：
   ```bash
   # 方式 1：使用启动脚本（推荐）
   # Windows PowerShell:
   .\run_streamlit.ps1
   
   # Windows CMD:
   run_streamlit.bat
   
   # 方式 2：使用 py 命令（Python Launcher）
   py -m streamlit run blog_to_podcast_agent.py
   
   # 方式 3：使用 python -m（确保不在虚拟环境中）
   python -m streamlit run blog_to_podcast_agent.py
   
   # 方式 4：如果 streamlit 命令在 PATH 中
   streamlit run blog_to_podcast_agent.py
   ```
   
   **常见问题**: 
   - ❌ `No module named streamlit`: 说明在虚拟环境中，请先运行 `deactivate` 退出虚拟环境
   - ❌ `streamlit: 无法识别`: 使用 `python -m streamlit` 或 `py -m streamlit` 方式运行
   - ✅ 推荐：退出虚拟环境后使用 `py -m streamlit run blog_to_podcast_agent.py`

2. 在浏览器中：
   - 在侧边栏输入 API Keys（如果未在 .env 中设置）
   - 输入要转换的博客 URL
   - 点击 "🎙️ Generate Podcast"
   - 播放生成的播客或下载

### 方式二：命令行 CLI（脚本化）

```bash
# 使用环境变量中的 API Keys
python blog_to_podcast_cli.py https://example.com/blog-post

# 手动指定 API Keys
python blog_to_podcast_cli.py https://example.com/blog-post \
  --openai-key sk-... \
  --elevenlabs-key ... \
  --firecrawl-key ...

# 指定输出文件名
python blog_to_podcast_cli.py https://example.com/blog-post -o my_podcast.mp3

# 查看帮助
python blog_to_podcast_cli.py --help
```

### 方式三：作为 Python 模块使用（编程式）

```python
from blog_to_podcast_core import BlogToPodcastConverter

# 创建转换器
converter = BlogToPodcastConverter(
    openai_api_key="your_openai_key",
    elevenlabs_api_key="your_elevenlabs_key",
    firecrawl_api_key="your_firecrawl_key"
)

# 转换博客为播客
summary, audio_bytes = converter.convert_blog_to_podcast(
    "https://example.com/blog-post"
)

# 保存音频
with open("podcast.mp3", "wb") as f:
    f.write(audio_bytes)
```

## 架构优势

✅ **解耦设计**: 核心业务逻辑 (`blog_to_podcast_core.py`) 完全不依赖 Streamlit  
✅ **灵活扩展**: 可以轻松添加新的 UI（如 FastAPI、Flask、Gradio 等）  
✅ **易于测试**: 核心逻辑可以独立测试，无需启动 Web 服务器  
✅ **多种使用场景**: 支持 Web UI、CLI、API 集成等多种使用方式