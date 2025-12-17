"""
数据存储层
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import Transaction, Budget, UserPreference


class DataStorage:
    """数据存储管理"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: 数据目录
        """
        self.data_dir = data_dir
        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.budgets_file = os.path.join(data_dir, "budgets.json")
        self.preferences_file = os.path.join(data_dir, "preferences.json")
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载数据
        self.transactions: List[Transaction] = self._load_transactions()
        self.budgets: Dict[str, Budget] = self._load_budgets()
        self.preferences: UserPreference = self._load_preferences()
    
    def _load_transactions(self) -> List[Transaction]:
        """加载交易记录"""
        if not os.path.exists(self.transactions_file):
            return []
        
        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Transaction.from_dict(t) for t in data]
        except Exception as e:
            print(f"⚠️ 加载交易记录失败：{e}")
            return []
    
    def _load_budgets(self) -> Dict[str, Budget]:
        """加载预算配置"""
        if not os.path.exists(self.budgets_file):
            return {}
        
        try:
            with open(self.budgets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: Budget.from_dict(v) for k, v in data.items()}
        except Exception as e:
            print(f"⚠️ 加载预算配置失败：{e}")
            return {}
    
    def _load_preferences(self) -> UserPreference:
        """加载用户偏好"""
        if not os.path.exists(self.preferences_file):
            return UserPreference()
        
        try:
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserPreference.from_dict(data)
        except Exception as e:
            print(f"⚠️ 加载用户偏好失败：{e}")
            return UserPreference()
    
    def _save_transactions(self):
        """保存交易记录"""
        try:
            data = [t.to_dict() for t in self.transactions]
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存交易记录失败：{e}")
    
    def _save_budgets(self):
        """保存预算配置"""
        try:
            data = {k: v.to_dict() for k, v in self.budgets.items()}
            with open(self.budgets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存预算配置失败：{e}")
    
    def _save_preferences(self):
        """保存用户偏好"""
        try:
            data = self.preferences.to_dict()
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存用户偏好失败：{e}")
    
    # ========== 交易记录操作 ==========
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """添加交易记录"""
        # 检查是否已存在
        if any(t.id == transaction.id for t in self.transactions):
            return False
        
        self.transactions.append(transaction)
        self.transactions.sort(key=lambda x: x.date, reverse=True)  # 按日期倒序
        self._save_transactions()
        return True
    
    def add_transactions(self, transactions: List[Transaction]) -> int:
        """批量添加交易记录"""
        added = 0
        for t in transactions:
            if self.add_transaction(t):
                added += 1
        return added
    
    def get_transactions(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Transaction]:
        """查询交易记录"""
        results = self.transactions
        
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if category:
            results = [t for t in results if t.category == category]
        if min_amount is not None:
            results = [t for t in results if abs(t.amount) >= min_amount]
        if max_amount is not None:
            results = [t for t in results if abs(t.amount) <= max_amount]
        
        return results
    
    def get_transactions_by_month(self, month: str) -> List[Transaction]:
        """获取指定月份的交易记录"""
        start_date = f"{month}-01"
        # 计算月末日期（简化处理）
        year, mon = month.split('-')
        if mon in ['01', '03', '05', '07', '08', '10', '12']:
            end_date = f"{month}-31"
        elif mon == '02':
            end_date = f"{month}-28"
        else:
            end_date = f"{month}-30"
        
        return self.get_transactions(start_date=start_date, end_date=end_date)
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """删除交易记录"""
        original_len = len(self.transactions)
        self.transactions = [t for t in self.transactions if t.id != transaction_id]
        if len(self.transactions) < original_len:
            self._save_transactions()
            return True
        return False
    
    # ========== 预算操作 ==========
    
    def set_budget(self, budget: Budget):
        """设置预算"""
        self.budgets[budget.month] = budget
        self._save_budgets()
    
    def get_budget(self, month: str) -> Optional[Budget]:
        """获取预算"""
        return self.budgets.get(month)
    
    # ========== 偏好操作 ==========
    
    def update_preferences(self, preferences: UserPreference):
        """更新用户偏好"""
        self.preferences = preferences
        self._save_preferences()
    
    def get_preferences(self) -> UserPreference:
        """获取用户偏好"""
        return self.preferences
    
    # ========== 统计方法 ==========
    
    def get_total_income(self, month: Optional[str] = None) -> float:
        """获取总收入"""
        transactions = self.get_transactions_by_month(month) if month else self.transactions
        return sum(t.amount for t in transactions if t.is_income())
    
    def get_total_expense(self, month: Optional[str] = None) -> float:
        """获取总支出"""
        transactions = self.get_transactions_by_month(month) if month else self.transactions
        return abs(sum(t.amount for t in transactions if t.is_expense()))
    
    def get_category_summary(self, month: Optional[str] = None) -> Dict[str, float]:
        """获取分类汇总"""
        transactions = self.get_transactions_by_month(month) if month else self.transactions
        summary = {}
        for t in transactions:
            if t.is_expense():
                category = t.category
                summary[category] = summary.get(category, 0) + abs(t.amount)
        return summary

