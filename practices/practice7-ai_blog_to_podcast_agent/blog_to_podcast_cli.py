"""
Blog to Podcast CLI 版本
不依赖 Streamlit，可以在命令行直接使用
"""
import os
import argparse
from dotenv import load_dotenv
from blog_to_podcast_core import BlogToPodcastConverter

# Load environment variables from .env file
load_dotenv()


def main():
    """CLI 主函数"""
    parser = argparse.ArgumentParser(
        description="将博客文章转换为播客音频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用环境变量中的 API Keys
  python blog_to_podcast_cli.py https://example.com/blog-post
  
  # 手动指定 API Keys
  python blog_to_podcast_cli.py https://example.com/blog-post \\
    --openai-key sk-... \\
    --elevenlabs-key ... \\
    --firecrawl-key ...
        """
    )
    
    parser.add_argument(
        "url",
        help="要转换的博客文章 URL"
    )
    
    parser.add_argument(
        "--openai-key",
        default=os.getenv("OPENAI_API_KEY", ""),
        help="OpenAI API Key (也可通过环境变量 OPENAI_API_KEY 设置)"
    )
    
    parser.add_argument(
        "--elevenlabs-key",
        default=os.getenv("ELEVENLABS_API_KEY", ""),
        help="ElevenLabs API Key (也可通过环境变量 ELEVENLABS_API_KEY 设置)"
    )
    
    parser.add_argument(
        "--firecrawl-key",
        default=os.getenv("FIRECRAWL_API_KEY", ""),
        help="Firecrawl API Key (也可通过环境变量 FIRECRAWL_API_KEY 设置)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="podcast.mp3",
        help="输出音频文件名 (默认: podcast.mp3)"
    )
    
    parser.add_argument(
        "--voice-id",
        default="JBFqnCBsd6RMkjVDRZzb",
        help="ElevenLabs 语音 ID (默认: JBFqnCBsd6RMkjVDRZzb)"
    )
    
    parser.add_argument(
        "--model-id",
        default="eleven_multilingual_v2",
        help="ElevenLabs 模型 ID (默认: eleven_multilingual_v2)"
    )
    
    args = parser.parse_args()
    
    # 验证 API Keys
    if not all([args.openai_key, args.elevenlabs_key, args.firecrawl_key]):
        parser.error("缺少必需的 API Keys。请通过命令行参数或环境变量提供。")
    
    try:
        print(f"📰 正在处理博客: {args.url}")
        print("⏳ 抓取内容并生成摘要...")
        
        # 创建转换器
        converter = BlogToPodcastConverter(
            openai_api_key=args.openai_key,
            elevenlabs_api_key=args.elevenlabs_key,
            firecrawl_api_key=args.firecrawl_key
        )
        
        # 转换博客为播客
        summary, audio_bytes = converter.convert_blog_to_podcast(
            args.url,
            voice_id=args.voice_id,
            model_id=args.model_id
        )
        
        # 保存音频文件
        with open(args.output, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ 播客生成成功！")
        print(f"📄 摘要 ({len(summary)} 字符):")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        print(f"🎧 音频已保存到: {args.output}")
        print(f"📊 音频大小: {len(audio_bytes) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=os.sys.stderr)
        os.sys.exit(1)


if __name__ == "__main__":
    main()

