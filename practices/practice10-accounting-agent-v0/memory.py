"""
记忆系统：短期记忆和长期记忆管理
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class ShortTermMemory:
    """短期记忆：当前对话上下文"""
    
    def __init__(self, max_turns: int = 20):
        self.conversations: List[Dict[str, str]] = []
        self.max_turns = max_turns
    
    def add(self, role: str, content: str):
        """添加对话"""
        self.conversations.append({"role": role, "content": content})
        
        # 限制长度
        if len(self.conversations) > self.max_turns * 2:
            self.conversations = self.conversations[-self.max_turns * 2:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取对话上下文"""
        return self.conversations.copy()
    
    def clear(self):
        """清空短期记忆"""
        self.conversations = []


class LongTermMemory:
    """长期记忆：用户偏好、历史查询、分析结果缓存"""
    
    def __init__(self, storage_path: str = "data/memory.json"):
        self.storage_path = storage_path
        self.memory: Dict[str, Any] = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """加载记忆"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _persist(self):
        """持久化记忆"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def save(self, key: str, value: Any):
        """保存记忆"""
        self.memory[key] = value
        self._persist()
    
    def retrieve(self, key: str) -> Optional[Any]:
        """检索记忆"""
        return self.memory.get(key)
    
    def save_user_preference(self, preference: Dict[str, Any]):
        """保存用户偏好"""
        if "preferences" not in self.memory:
            self.memory["preferences"] = {}
        self.memory["preferences"].update(preference)
        self._persist()
    
    def get_user_preference(self, key: str) -> Optional[Any]:
        """获取用户偏好"""
        return self.memory.get("preferences", {}).get(key)
    
    def save_query_history(self, query: str, result: str):
        """保存查询历史"""
        if "query_history" not in self.memory:
            self.memory["query_history"] = []
        
        self.memory["query_history"].append({
            "query": query,
            "result": result[:500],  # 限制长度
            "timestamp": datetime.now().isoformat()
        })
        
        # 只保留最近50条
        if len(self.memory["query_history"]) > 50:
            self.memory["query_history"] = self.memory["query_history"][-50:]
        
        self._persist()
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的查询"""
        history = self.memory.get("query_history", [])
        return history[-limit:]
    
    def save_analysis_cache(self, key: str, analysis: str):
        """缓存分析结果"""
        if "analysis_cache" not in self.memory:
            self.memory["analysis_cache"] = {}
        
        self.memory["analysis_cache"][key] = {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        # 限制缓存大小
        if len(self.memory["analysis_cache"]) > 20:
            # 删除最旧的
            oldest_key = min(
                self.memory["analysis_cache"].keys(),
                key=lambda k: self.memory["analysis_cache"][k]["timestamp"]
            )
            del self.memory["analysis_cache"][oldest_key]
        
        self._persist()
    
    def get_analysis_cache(self, key: str) -> Optional[str]:
        """获取缓存的分析结果"""
        cache = self.memory.get("analysis_cache", {}).get(key)
        return cache.get("analysis") if cache else None

