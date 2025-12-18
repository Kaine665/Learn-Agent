"""
Blog to Podcast Streamlit UI
使用 blog_to_podcast_core 模块处理业务逻辑
"""
import os
import sys
import site

# 添加用户 site-packages 目录到 Python 路径（用于访问 --user 安装的包，如 elevenlabs）
# 这样可以解决虚拟环境中无法安装 elevenlabs（路径长度限制）的问题
user_site_packages = site.getusersitepackages()
if user_site_packages and user_site_packages not in sys.path:
    sys.path.insert(0, user_site_packages)

import streamlit as st
from dotenv import load_dotenv
from blog_to_podcast_core import BlogToPodcastConverter

# Load environment variables from .env file
load_dotenv()

# Streamlit Setup
st.set_page_config(page_title="📰 ➡️ 🎙️ Blog to Podcast", page_icon="🎙️")
st.title("📰 ➡️ 🎙️ Blog to Podcast Agent")

# API Keys - 优先使用环境变量，如果没有则从界面输入
st.sidebar.header("🔑 API Keys")
st.sidebar.caption("💡 提示：可以在 .env 文件中设置，或在此处输入")

# 从环境变量获取，如果没有则从界面输入
openai_key_env = os.getenv("OPENAI_API_KEY", "")
elevenlabs_key_env = os.getenv("ELEVENLABS_API_KEY", "")
firecrawl_key_env = os.getenv("FIRECRAWL_API_KEY", "")

openai_key = st.sidebar.text_input(
    "OpenAI API Key", 
    value=openai_key_env if openai_key_env else "",
    type="password",
    help="从 https://platform.openai.com/api-keys 获取"
)
elevenlabs_key = st.sidebar.text_input(
    "ElevenLabs API Key", 
    value=elevenlabs_key_env if elevenlabs_key_env else "",
    type="password",
    help="从 https://elevenlabs.io/app/settings/api-keys 获取"
)
firecrawl_key = st.sidebar.text_input(
    "Firecrawl API Key", 
    value=firecrawl_key_env if firecrawl_key_env else "",
    type="password",
    help="从 https://firecrawl.dev 获取"
)

# Blog URL Input
url = st.text_input("Enter Blog URL:", "")

# Generate Button
if st.button("🎙️ Generate Podcast", disabled=not all([openai_key, elevenlabs_key, firecrawl_key])):
    if not url.strip():
        st.warning("Please enter a blog URL")
    else:
        with st.spinner("Scraping blog and generating podcast..."):
            try:
                # 使用核心模块进行转换
                converter = BlogToPodcastConverter(
                    openai_api_key=openai_key,
                    elevenlabs_api_key=elevenlabs_key,
                    firecrawl_api_key=firecrawl_key
                )
                
                summary, audio_bytes = converter.convert_blog_to_podcast(url)
                
                # Display audio
                st.success("Podcast generated! 🎧")
                st.audio(audio_bytes, format="audio/mp3")
                
                # Download button
                st.download_button(
                    "Download Podcast",
                    audio_bytes,
                    "podcast.mp3",
                    "audio/mp3"
                )
                
                # Show summary
                with st.expander("📄 Podcast Summary"):
                    st.write(summary)
                    
            except Exception as e:
                st.error(f"Error: {e}")
