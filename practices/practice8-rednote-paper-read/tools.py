"""
工具系统：网页抓取、OCR等工具
"""

import re
import requests
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from datetime import datetime


class WebScraperTool:
    """网页抓取工具（简单版本）"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        抓取网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            包含标题、内容等的字典
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = ""
            if soup.title:
                title = soup.title.string.strip()
            
            # 提取正文（简单提取，小红书可能需要特殊处理）
            content = ""
            # 尝试提取meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                content = meta_desc.get('content')
            else:
                # 提取所有文本
                content = soup.get_text(separator='\n', strip=True)
                # 限制长度
                content = content[:5000]
            
            return {
                'success': True,
                'title': title,
                'content': content,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }


class XiaohongshuURLParser:
    """小红书URL解析工具"""
    
    @staticmethod
    def extract_post_id(url: str) -> Optional[str]:
        """
        从小红书URL中提取帖子ID
        
        Args:
            url: 小红书帖子URL
            
        Returns:
            帖子ID或None
        """
        # 小红书URL格式示例：
        # https://www.xiaohongshu.com/explore/xxxxx
        # https://www.xiaohongshu.com/discovery/item/xxxxx
        
        patterns = [
            r'/explore/([a-zA-Z0-9]+)',
            r'/discovery/item/([a-zA-Z0-9]+)',
            r'/user/profile/([a-zA-Z0-9]+)/notes/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(2)
        
        return None
    
    @staticmethod
    def is_xiaohongshu_url(url: str) -> bool:
        """判断是否为小红书URL"""
        return 'xiaohongshu.com' in url.lower() or 'xhslink.com' in url.lower()


class SimpleOCRTool:
    """简单的OCR工具（占位实现）
    
    注意：这是一个简化版本。如果需要真正的OCR功能，可以：
    1. 使用 PaddleOCR（中文效果好，但需要安装）
    2. 使用 Tesseract（需要安装）
    3. 使用在线OCR API（如百度OCR、腾讯OCR等）
    """
    
    def __init__(self):
        self.available = False
        # 这里可以初始化OCR库，但为了简单，先不实现
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            提取的文字
        """
        # TODO: 实现OCR功能
        # 可以使用 PaddleOCR:
        # from paddleocr import PaddleOCR
        # ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        # result = ocr.ocr(image_path, cls=True)
        # text = '\n'.join([line[1][0] for line in result[0]])
        
        return f"[OCR功能未实现] 图片路径: {image_path}"
    
    def extract_text_from_screenshot(self, screenshot_path: str) -> str:
        """从截图中提取文字"""
        return self.extract_text_from_image(screenshot_path)


class ManualInputTool:
    """手动输入工具（用于截图后手动输入内容）"""
    
    @staticmethod
    def create_post_from_manual_input(
        title: str,
        content: str,
        author: str = "未知",
        post_type: str = "image",
        original_link: str = ""
    ) -> Dict[str, Any]:
        """
        从手动输入创建帖子数据
        
        Args:
            title: 标题
            content: 内容
            author: 作者
            post_type: 类型（image/video）
            original_link: 原链接
            
        Returns:
            帖子数据字典
        """
        post_id = f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'post_id': post_id,
            'title': title,
            'content': content,
            'author': author,
            'post_type': post_type,
            'images': [],
            'video_url': None,
            'original_link': original_link,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'likes': 0,
            'comments': 0,
            'collected': 0
        }

