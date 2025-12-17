"""
数据模型定义
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class Transaction:
    """交易记录"""
    date: str  # YYYY-MM-DD
    amount: float  # 金额（正数为收入，负数为支出）
    category: str  # 类别（如：餐饮、交通、购物等）
    description: str  # 描述
    tags: list = None  # 标签
    id: Optional[str] = None  # 唯一ID
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.id is None:
            self.id = f"{self.date}_{hash(self.description)}_{abs(self.amount)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """从字典创建"""
        return cls(**data)
    
    def is_income(self) -> bool:
        """是否为收入"""
        return self.amount > 0
    
    def is_expense(self) -> bool:
        """是否为支出"""
        return self.amount < 0


@dataclass
class Budget:
    """预算配置"""
    month: str  # YYYY-MM
    total_budget: float  # 总预算
    category_budgets: Dict[str, float] = None  # 分类预算
    
    def __post_init__(self):
        if self.category_budgets is None:
            self.category_budgets = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """从字典创建"""
        return cls(**data)


@dataclass
class UserPreference:
    """用户偏好"""
    default_categories: list = None  # 默认分类
    currency: str = "CNY"  # 货币单位
    date_format: str = "YYYY-MM-DD"  # 日期格式
    
    def __post_init__(self):
        if self.default_categories is None:
            self.default_categories = [
                "餐饮", "交通", "购物", "娱乐", "医疗", 
                "教育", "住房", "其他", "收入"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreference':
        """从字典创建"""
        return cls(**data)

