"""
提示词加载器：从JSON文件加载提示词（key-value管理）
"""

import json
from pathlib import Path
from typing import Dict


class PromptLoader:
    """
    提示词加载器：使用key-value方式管理提示词
    
    设计：
    - key：简短精要的中文描述（如："布局分析"）
    - value：具体的提示词内容
    - 所有提示词存储在 prompts.json 中统一管理
    """
    
    def __init__(self, prompts_dir: str = None):
        """
        初始化提示词加载器
        
        Args:
            prompts_dir: 提示词目录路径，默认使用 prompts/ 目录
        """
        if prompts_dir is None:
            # 获取当前文件所在目录的 prompts 子目录
            current_file = Path(__file__).parent
            prompts_dir = current_file
        
        self.prompts_dir = Path(prompts_dir)
        self.prompts_json_path = self.prompts_dir / "prompts.json"
        
        # 加载提示词表
        self._prompts: Dict[str, str] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """从JSON文件加载所有提示词"""
        if self.prompts_json_path.exists():
            try:
                with open(self.prompts_json_path, "r", encoding="utf-8-sig") as f:
                    self._prompts = json.load(f)
            except Exception as e:
                raise ValueError(f"加载提示词表失败：{e}")
        else:
            # 如果JSON文件不存在，创建空表
            self._prompts = {}
            self._save_prompts()
    
    def _save_prompts(self):
        """保存提示词表到JSON文件"""
        with open(self.prompts_json_path, "w", encoding="utf-8") as f:
            json.dump(self._prompts, f, ensure_ascii=False, indent=2)
    
    def load(self, prompt_key: str) -> str:
        """
        根据key加载提示词
        
        Args:
            prompt_key: 提示词的key（简短的中文描述，如："布局分析"）
        
        Returns:
            提示词内容
        
        Raises:
            KeyError: 如果key不存在
        """
        if prompt_key not in self._prompts:
            available_keys = ", ".join(self._prompts.keys())
            raise KeyError(
                f"提示词key不存在：'{prompt_key}'\n"
                f"可用的key：{available_keys if available_keys else '无'}"
            )
        
        return self._prompts[prompt_key]
    
    def list_keys(self) -> list:
        """
        列出所有可用的提示词key
        
        Returns:
            key列表
        """
        return list(self._prompts.keys())
    
    def add(self, key: str, value: str):
        """
        添加或更新提示词
        
        Args:
            key: 提示词的key（简短的中文描述）
            value: 提示词内容
        """
        self._prompts[key] = value
        self._save_prompts()
    
    def remove(self, key: str):
        """
        删除提示词
        
        Args:
            key: 要删除的提示词key
        """
        if key in self._prompts:
            del self._prompts[key]
            self._save_prompts()
        else:
            raise KeyError(f"提示词key不存在：'{key}'")

