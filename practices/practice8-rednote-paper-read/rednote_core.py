"""
小红书帖子阅读核心模块
处理帖子获取、内容提取等核心业务逻辑
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
from models import RednotePost
from tools import WebScraperTool, XiaohongshuURLParser, ManualInputTool


class RednotePostFetcher:
    """小红书帖子获取器"""
    
    def __init__(self):
        self.scraper = WebScraperTool()
        self.url_parser = XiaohongshuURLParser()
        self.manual_tool = ManualInputTool()
    
    def fetch_post_from_url(self, url: str) -> Optional[RednotePost]:
        """
        从URL获取小红书帖子
        
        Args:
            url: 小红书帖子URL
            
        Returns:
            RednotePost对象或None
        """
        # 提取帖子ID
        post_id = self.url_parser.extract_post_id(url)
        if not post_id:
            # 如果无法提取ID，使用时间戳
            post_id = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 抓取网页内容
        result = self.scraper.scrape_url(url)
        
        if not result.get('success'):
            print(f"⚠️ 抓取失败：{result.get('error', '未知错误')}")
            return None
        
        # 解析内容
        title = result.get('title', '无标题')
        content = result.get('content', '')
        
        # 尝试从URL或内容中提取更多信息
        # 这里简化处理，实际可能需要更复杂的解析
        
        post = RednotePost(
            post_id=post_id,
            title=title,
            content=content[:2000] if len(content) > 2000 else content,  # 限制长度
            author="未知",
            post_type="image",  # 默认图文，实际需要判断
            images=[],
            video_url=None,
            original_link=url,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            likes=0,
            comments=0,
            collected=0
        )
        
        return post
    
    def create_post_from_manual(self, title: str, content: str, 
                                author: str = "未知", 
                                post_type: str = "image",
                                original_link: str = "") -> RednotePost:
        """
        从手动输入创建帖子（用于截图后手动输入的场景）
        
        Args:
            title: 标题
            content: 内容
            author: 作者
            post_type: 类型
            original_link: 原链接
            
        Returns:
            RednotePost对象
        """
        data = self.manual_tool.create_post_from_manual_input(
            title=title,
            content=content,
            author=author,
            post_type=post_type,
            original_link=original_link
        )
        
        return RednotePost(**data)
    
    def fetch_post(self, source: str, **kwargs) -> Optional[RednotePost]:
        """
        通用获取帖子方法
        
        Args:
            source: 来源（'url' 或 'manual'）
            **kwargs: 其他参数
            
        Returns:
            RednotePost对象或None
        """
        if source == 'url':
            url = kwargs.get('url', '')
            if not url:
                print("❌ 缺少URL参数")
                return None
            return self.fetch_post_from_url(url)
        
        elif source == 'manual':
            title = kwargs.get('title', '')
            content = kwargs.get('content', '')
            if not title and not content:
                print("❌ 缺少标题或内容")
                return None
            return self.create_post_from_manual(
                title=title,
                content=content,
                author=kwargs.get('author', '未知'),
                post_type=kwargs.get('post_type', 'image'),
                original_link=kwargs.get('original_link', '')
            )
        
        else:
            print(f"❌ 不支持的来源类型：{source}")
            return None

