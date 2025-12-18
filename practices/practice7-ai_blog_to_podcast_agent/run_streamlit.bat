@echo off
REM 使用系统 Python 运行 Streamlit（因为虚拟环境无法安装 elevenlabs 包）
REM 注意：如果当前在虚拟环境中，请先退出：deactivate

REM 尝试使用 py 命令（Python Launcher）
py -m streamlit run blog_to_podcast_agent.py
if %ERRORLEVEL% EQU 0 exit /b 0

REM 如果 py 不可用，尝试直接使用 python（需要确保不在虚拟环境中）
python -m streamlit run blog_to_podcast_agent.py

