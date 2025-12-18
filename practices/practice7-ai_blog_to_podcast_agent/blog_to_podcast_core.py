"""
Blog to Podcast 核心业务逻辑模块
不依赖任何 UI 框架，可以独立使用
"""
import os
import sys
import site

# 添加用户 site-packages 目录到 Python 路径（用于访问 --user 安装的包，如 elevenlabs）
# 这样可以解决虚拟环境中无法安装 elevenlabs（路径长度限制）的问题
user_site_packages = site.getusersitepackages()
if user_site_packages and user_site_packages not in sys.path:
    sys.path.insert(0, user_site_packages)

from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from elevenlabs import ElevenLabs
from typing import Optional, Tuple


class BlogToPodcastConverter:
    """博客转播客转换器核心类"""
    
    def __init__(
        self,
        openai_api_key: str,
        elevenlabs_api_key: str,
        firecrawl_api_key: str
    ):
        """
        初始化转换器
        
        Args:
            openai_api_key: OpenAI API Key
            elevenlabs_api_key: ElevenLabs API Key
            firecrawl_api_key: Firecrawl API Key
        """
        self.openai_api_key = openai_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.firecrawl_api_key = firecrawl_api_key
        
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key
    
    def scrape_and_summarize(self, blog_url: str) -> str:
        """
        抓取博客内容并生成摘要
        
        Args:
            blog_url: 博客 URL
            
        Returns:
            摘要文本
            
        Raises:
            Exception: 如果抓取或摘要生成失败
        """
        # 创建 agent 用于抓取和摘要
        agent = Agent(
            name="Blog Summarizer",
            model=OpenAIChat(id="gpt-4o"),
            tools=[FirecrawlTools()],
            instructions=[
                "Scrape the blog URL and create a concise, engaging summary (max 2000 characters) suitable for a podcast.",
                "The summary should be conversational and capture the main points."
            ],
        )
        
        # 获取摘要
        response: RunOutput = agent.run(f"Scrape and summarize this blog for a podcast: {blog_url}")
        summary = response.content if hasattr(response, 'content') else str(response)
        
        if not summary:
            raise ValueError("Failed to generate summary")
        
        return summary
    
    def generate_audio(
        self,
        text: str,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
        model_id: str = "eleven_multilingual_v2"
    ) -> bytes:
        """
        将文本转换为音频
        
        Args:
            text: 要转换的文本
            voice_id: ElevenLabs 语音 ID
            model_id: ElevenLabs 模型 ID
            
        Returns:
            音频字节数据
            
        Raises:
            Exception: 如果音频生成失败
        """
        # 初始化 ElevenLabs 客户端
        client = ElevenLabs(api_key=self.elevenlabs_api_key)
        
        # 生成音频
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id
        )
        
        # 收集音频块
        audio_chunks = []
        for chunk in audio_generator:
            if chunk:
                audio_chunks.append(chunk)
        
        return b"".join(audio_chunks)
    
    def convert_blog_to_podcast(
        self,
        blog_url: str,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
        model_id: str = "eleven_multilingual_v2"
    ) -> Tuple[str, bytes]:
        """
        完整的博客转播客流程
        
        Args:
            blog_url: 博客 URL
            voice_id: ElevenLabs 语音 ID
            model_id: ElevenLabs 模型 ID
            
        Returns:
            (摘要文本, 音频字节数据) 元组
            
        Raises:
            Exception: 如果转换过程中出现错误
        """
        # 1. 抓取并生成摘要
        summary = self.scrape_and_summarize(blog_url)
        
        # 2. 生成音频
        audio_bytes = self.generate_audio(summary, voice_id, model_id)
        
        return summary, audio_bytes


def convert_blog_to_podcast(
    blog_url: str,
    openai_api_key: str,
    elevenlabs_api_key: str,
    firecrawl_api_key: str,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2"
) -> Tuple[str, bytes]:
    """
    便捷函数：将博客转换为播客
    
    Args:
        blog_url: 博客 URL
        openai_api_key: OpenAI API Key
        elevenlabs_api_key: ElevenLabs API Key
        firecrawl_api_key: Firecrawl API Key
        voice_id: ElevenLabs 语音 ID
        model_id: ElevenLabs 模型 ID
        
    Returns:
        (摘要文本, 音频字节数据) 元组
    """
    converter = BlogToPodcastConverter(
        openai_api_key=openai_api_key,
        elevenlabs_api_key=elevenlabs_api_key,
        firecrawl_api_key=firecrawl_api_key
    )
    return converter.convert_blog_to_podcast(blog_url, voice_id, model_id)

