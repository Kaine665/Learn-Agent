"""
数据模型定义
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class RednotePost:
    """小红书帖子模型"""
    post_id: str                    # 帖子ID
    title: str                      # 标题
    content: str                    # 正文内容
    author: str                     # 作者
    post_type: str                  # 类型：'image' 或 'video'
    images: List[str]               # 图片URL列表
    video_url: Optional[str]        # 视频URL（如果是视频）
    original_link: str              # 原链接（可跳转）
    created_at: str                 # 创建时间（字符串格式：YYYY-MM-DD HH:MM:SS）
    likes: int = 0                  # 点赞数
    comments: int = 0               # 评论数
    collected: int = 0             # 收藏数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RednotePost':
        """从字典创建"""
        return cls(**data)


@dataclass
class PostSummary:
    """帖子摘要"""
    post_id: str
    summary: str                    # AI生成的摘要
    key_points: List[str]           # 关键点
    tags: List[str]                 # 标签
    created_at: str                 # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostSummary':
        """从字典创建"""
        return cls(**data)


@dataclass
class UserNote:
    """用户批注"""
    post_id: str
    note: str                       # 批注内容
    created_at: str                 # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserNote':
        """从字典创建"""
        return cls(**data)


@dataclass
class ReadingStatus:
    """阅读状态"""
    post_id: str
    is_read: bool = False           # 是否已读
    read_at: Optional[str] = None   # 阅读时间
    rating: Optional[int] = None    # 评分（1-5）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReadingStatus':
        """从字典创建"""
        return cls(**data)

