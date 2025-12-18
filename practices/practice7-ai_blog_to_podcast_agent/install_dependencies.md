# 安装依赖说明

## 方法一：在虚拟环境中安装（推荐，除了 elevenlabs）

由于 Windows 路径长度限制，`elevenlabs` 包无法安装到虚拟环境，但其他包都可以正常安装。

### PowerShell 方式：

```powershell
# 1. 激活虚拟环境（如果还没激活）
cd C:\Users\17130\Desktop\ProgrammingProjects\personal-projects\Learn-Agent
.\venv\Scripts\Activate.ps1

# 2. 进入项目目录
cd practices\practice7-ai_blog_to_podcast_agent

# 3. 安装除 elevenlabs 外的所有依赖
python -m pip install streamlit agno openai requests firecrawl-py python-dotenv

# 或者从 requirements.txt 安装（会跳过 elevenlabs）
python -m pip install streamlit agno openai requests firecrawl-py python-dotenv
```

### CMD 方式：

```cmd
REM 1. 激活虚拟环境
cd C:\Users\17130\Desktop\ProgrammingProjects\personal-projects\Learn-Agent
venv\Scripts\activate.bat

REM 2. 进入项目目录
cd practices\practice7-ai_blog_to_podcast_agent

REM 3. 安装依赖
python -m pip install streamlit agno openai requests firecrawl-py python-dotenv
```

## 方法二：安装 elevenlabs（使用 --user）

由于路径长度限制，`elevenlabs` 需要安装到用户目录：

```powershell
# PowerShell 或 CMD
pip install --user elevenlabs
```

## 验证安装

```powershell
# 在虚拟环境中验证
python -c "import streamlit; print('Streamlit 安装成功！')"
python -c "import agno; print('Agno 安装成功！')"
python -c "import elevenlabs; print('ElevenLabs 安装成功！')"  # 这个会从用户目录加载
```

## 运行应用

安装完成后，在虚拟环境中运行：

```powershell
# 确保在虚拟环境中（提示符显示 (.venv)）
python -m streamlit run blog_to_podcast_agent.py
```

**注意**: `elevenlabs` 会从用户目录加载，即使虚拟环境中没有安装也能正常工作。

