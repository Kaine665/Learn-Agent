"""
数据存储层
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import RednotePost, PostSummary, UserNote, ReadingStatus


class RednoteStorage:
    """小红书帖子数据存储管理"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir
        self.posts_file = os.path.join(data_dir, "posts.json")
        self.summaries_file = os.path.join(data_dir, "summaries.json")
        self.notes_file = os.path.join(data_dir, "notes.json")
        self.status_file = os.path.join(data_dir, "reading_status.json")
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载数据
        self.posts: List[RednotePost] = self._load_posts()
        self.summaries: Dict[str, PostSummary] = self._load_summaries()
        self.notes: Dict[str, List[UserNote]] = self._load_notes()
        self.status: Dict[str, ReadingStatus] = self._load_status()
    
    def _load_posts(self) -> List[RednotePost]:
        """加载帖子列表"""
        if not os.path.exists(self.posts_file):
            return []
        
        try:
            with open(self.posts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [RednotePost.from_dict(p) for p in data]
        except Exception as e:
            print(f"⚠️ 加载帖子列表失败：{e}")
            return []
    
    def _load_summaries(self) -> Dict[str, PostSummary]:
        """加载摘要"""
        if not os.path.exists(self.summaries_file):
            return {}
        
        try:
            with open(self.summaries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: PostSummary.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"⚠️ 加载摘要失败：{e}")
            return {}
    
    def _load_notes(self) -> Dict[str, List[UserNote]]:
        """加载批注"""
        if not os.path.exists(self.notes_file):
            return {}
        
        try:
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result = {}
                for post_id, notes_list in data.items():
                    result[post_id] = [UserNote.from_dict(n) for n in notes_list]
                return result
        except Exception as e:
            print(f"⚠️ 加载批注失败：{e}")
            return {}
    
    def _load_status(self) -> Dict[str, ReadingStatus]:
        """加载阅读状态"""
        if not os.path.exists(self.status_file):
            return {}
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: ReadingStatus.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"⚠️ 加载阅读状态失败：{e}")
            return {}
    
    def _save_posts(self):
        """保存帖子列表"""
        try:
            data = [p.to_dict() for p in self.posts]
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存帖子列表失败：{e}")
    
    def _save_summaries(self):
        """保存摘要"""
        try:
            data = {k: v.to_dict() for k, v in self.summaries.items()}
            with open(self.summaries_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存摘要失败：{e}")
    
    def _save_notes(self):
        """保存批注"""
        try:
            data = {}
            for post_id, notes_list in self.notes.items():
                data[post_id] = [n.to_dict() for n in notes_list]
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存批注失败：{e}")
    
    def _save_status(self):
        """保存阅读状态"""
        try:
            data = {k: v.to_dict() for k, v in self.status.items()}
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存阅读状态失败：{e}")
    
    # ========== 帖子操作 ==========
    
    def add_post(self, post: RednotePost) -> bool:
        """添加帖子"""
        # 检查是否已存在
        if any(p.post_id == post.post_id for p in self.posts):
            return False
        
        self.posts.append(post)
        self.posts.sort(key=lambda x: x.created_at, reverse=True)  # 按时间倒序
        self._save_posts()
        return True
    
    def get_post(self, post_id: str) -> Optional[RednotePost]:
        """获取帖子"""
        for post in self.posts:
            if post.post_id == post_id:
                return post
        return None
    
    def get_all_posts(self) -> List[RednotePost]:
        """获取所有帖子"""
        return self.posts
    
    def get_unread_posts(self) -> List[RednotePost]:
        """获取未读帖子"""
        unread_ids = set()
        for post_id, status in self.status.items():
            if not status.is_read:
                unread_ids.add(post_id)
        
        # 如果状态中没有记录，也视为未读
        all_post_ids = {p.post_id for p in self.posts}
        unread_ids.update(all_post_ids - set(self.status.keys()))
        
        return [p for p in self.posts if p.post_id in unread_ids]
    
    # ========== 摘要操作 ==========
    
    def save_summary(self, summary: PostSummary):
        """保存摘要"""
        self.summaries[summary.post_id] = summary
        self._save_summaries()
    
    def get_summary(self, post_id: str) -> Optional[PostSummary]:
        """获取摘要"""
        return self.summaries.get(post_id)
    
    # ========== 批注操作 ==========
    
    def add_note(self, post_id: str, note: str):
        """添加批注"""
        if post_id not in self.notes:
            self.notes[post_id] = []
        
        new_note = UserNote(
            post_id=post_id,
            note=note,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.notes[post_id].append(new_note)
        self._save_notes()
    
    def get_notes(self, post_id: str) -> List[UserNote]:
        """获取批注"""
        return self.notes.get(post_id, [])
    
    # ========== 阅读状态操作 ==========
    
    def mark_as_read(self, post_id: str, rating: Optional[int] = None):
        """标记为已读"""
        self.status[post_id] = ReadingStatus(
            post_id=post_id,
            is_read=True,
            read_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rating=rating
        )
        self._save_status()
    
    def get_status(self, post_id: str) -> Optional[ReadingStatus]:
        """获取阅读状态"""
        return self.status.get(post_id)

