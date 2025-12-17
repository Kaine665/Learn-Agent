"""
工具系统：文件解析、数据查询、统计分析
"""

import csv
import json
import re
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from models import Transaction
from storage import DataStorage

# Excel支持
try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

# 文件转换框架
try:
    from file_converter import FileConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False

# 文件转换框架
try:
    from file_converter import FileConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False


class Tool:
    """工具基类"""
    
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, *args, **kwargs) -> Any:
        """执行工具"""
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class FileParserTool:
    """文件解析工具"""
    
    @staticmethod
    def parse_csv(file_path: str) -> List[Transaction]:
        """解析CSV文件"""
        transactions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 尝试从不同列名读取数据
                    date = row.get('date') or row.get('日期') or row.get('Date')
                    amount_str = row.get('amount') or row.get('金额') or row.get('Amount')
                    category = row.get('category') or row.get('类别') or row.get('Category')
                    description = row.get('description') or row.get('描述') or row.get('Description')
                    
                    if not all([date, amount_str, category, description]):
                        continue
                    
                    try:
                        amount = float(amount_str)
                        # 如果金额为正，但应该是支出，则转为负数
                        # 这里可以根据实际需求调整逻辑
                        transaction = Transaction(
                            date=date,
                            amount=amount,
                            category=category,
                            description=description
                        )
                        transactions.append(transaction)
                    except ValueError:
                        continue
        except Exception as e:
            raise Exception(f"CSV解析失败：{str(e)}")
        
        return transactions
    
    @staticmethod
    def parse_json(file_path: str) -> List[Transaction]:
        """解析JSON文件"""
        transactions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        transaction = Transaction.from_dict(item)
                        transactions.append(transaction)
                elif isinstance(data, dict) and 'transactions' in data:
                    for item in data['transactions']:
                        transaction = Transaction.from_dict(item)
                        transactions.append(transaction)
        except Exception as e:
            raise Exception(f"JSON解析失败：{str(e)}")
        
        return transactions
    
    @staticmethod
    def parse_excel(file_path: str, api_key: Optional[str] = None) -> List[Transaction]:
        """
        解析Excel文件（.xlsx），使用智能转换框架
        
        Args:
            file_path: 文件路径
            api_key: OpenAI API Key（用于交互式学习，可选）
        """
        if not EXCEL_SUPPORT:
            raise Exception("需要安装openpyxl库：pip install openpyxl")
        
        # 🔥 优先使用新的文件转换框架
        if CONVERTER_AVAILABLE:
            try:
                converter = FileConverter(api_key=api_key)
                success, transactions, message = converter.convert(file_path, interactive=False)
                
                if success:
                    print(f"✅ {message}")
                    return transactions
                else:
                    print(f"⚠️ {message}")
                    # 如果转换框架失败，回退到旧方法
                    print("🔄 回退到传统解析方法...")
            except Exception as e:
                print(f"⚠️ 文件转换框架出错：{e}")
                print("🔄 回退到传统解析方法...")
        
        # 回退到传统解析方法（保持向后兼容）
        return FileParserTool._parse_excel_legacy(file_path)
    
    @staticmethod
    def _parse_excel_legacy(file_path: str) -> List[Transaction]:
        """传统Excel解析方法（保持向后兼容）"""
        transactions = []
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(file_path)
            ws = wb.active  # 使用第一个工作表
            
            # 读取表头，找到列索引
            header_row = None
            date_col = None
            amount_col = None
            type_col = None  # 交易类型列（用于判断收入/支出）
            category_col = None
            description_col = None
            counterparty_col = None  # 交易对方列
            product_col = None  # 商品列
            
            # 查找表头行（扩大搜索范围，跳过前面的元数据）
            # 微信账单通常表头在第10-30行之间
            for row_idx in range(1, min(50, ws.max_row + 1)):
                row = [cell.value for cell in ws[row_idx]]
                row_str = ' '.join([str(cell).strip() for cell in row if cell]).lower()
                
                # 跳过明显的元数据行
                if any(keyword in row_str for keyword in ['微信支付账单明细', '起始时间', '终止时间', '导出类型', '导出时间', '共', '笔记录', '收入:', '支出:', '中性交易:', '注:']):
                    continue
                
                # 重置列索引
                date_col = None
                amount_col = None
                type_col = None
                category_col = None
                description_col = None
                counterparty_col = None
                product_col = None
                
                # 尝试找到包含日期、金额等关键词的列
                for col_idx, cell_value in enumerate(row):
                    if not cell_value:
                        continue
                    
                    cell_str = str(cell_value).strip()
                    cell_str_lower = cell_str.lower()
                    
                    # 匹配各种可能的列名
                    if '交易时间' in cell_str or '时间' in cell_str or 'date' in cell_str_lower or 'time' in cell_str_lower:
                        date_col = col_idx
                    elif '收/支金额' in cell_str or '金额' in cell_str or 'amount' in cell_str_lower or 'money' in cell_str_lower:
                        amount_col = col_idx
                    elif '交易类型' in cell_str or '类型' in cell_str or 'type' in cell_str_lower:
                        type_col = col_idx
                    elif '类别' in cell_str or 'category' in cell_str_lower or '分类' in cell_str:
                        category_col = col_idx
                    elif '商品' in cell_str or 'product' in cell_str_lower:
                        product_col = col_idx
                    elif '交易对方' in cell_str or '对方' in cell_str or 'counterparty' in cell_str_lower:
                        counterparty_col = col_idx
                    elif '描述' in cell_str or 'description' in cell_str_lower or '备注' in cell_str or '说明' in cell_str:
                        description_col = col_idx
                
                # 如果找到了日期和金额列，这就是表头行
                if date_col is not None and amount_col is not None:
                    header_row = row_idx
                    break
            
            if header_row is None:
                # 如果没找到，尝试更宽松的匹配
                for row_idx in range(1, min(50, ws.max_row + 1)):
                    row = [cell.value for cell in ws[row_idx]]
                    row_str = ' '.join([str(cell).strip() for cell in row if cell]).lower()
                    
                    # 检查是否包含表头关键词
                    if '交易时间' in row_str and ('金额' in row_str or '金额' in row_str):
                        # 重新解析这一行
                        for col_idx, cell_value in enumerate(row):
                            if not cell_value:
                                continue
                            cell_str = str(cell_value).strip().lower()
                            if '交易时间' in cell_str or '时间' in cell_str:
                                date_col = col_idx
                            elif '收/支金额' in cell_str or '金额' in cell_str:
                                amount_col = col_idx
                            elif '交易类型' in cell_str or '类型' in cell_str:
                                type_col = col_idx
                            elif '商品' in cell_str:
                                product_col = col_idx
                            elif '交易对方' in cell_str or '对方' in cell_str:
                                counterparty_col = col_idx
                        
                        if date_col is not None and amount_col is not None:
                            header_row = row_idx
                            break
            
            if header_row is None:
                raise Exception("无法找到表头行。请确保Excel文件包含'交易时间'和'金额'列。\n提示：微信账单的表头通常在数据区域的第一行。")
            
            # 读取数据行
            for row_idx in range(header_row + 1, ws.max_row + 1):
                row = [cell.value for cell in ws[row_idx]]
                
                # 跳过空行
                if not any(row):
                    continue
                
                # 跳过明显的分隔行或元数据行
                first_cell = str(row[0]).strip() if row and row[0] else ""
                if not first_cell or first_cell.startswith('注') or '微信支付' in first_cell:
                    continue
                
                # 提取数据
                date_value = row[date_col] if date_col < len(row) else None
                amount_value = row[amount_col] if amount_col < len(row) else None
                
                # 获取交易类型（用于判断收入/支出）
                type_value = None
                if type_col is not None and type_col < len(row):
                    type_value = str(row[type_col]).strip() if row[type_col] else None
                
                # 获取类别（如果没有交易类型列，尝试从其他列推断）
                category_value = None
                if category_col is not None and category_col < len(row):
                    category_value = str(row[category_col]).strip() if row[category_col] else None
                
                # 获取描述（优先使用商品列，其次交易对方列，最后描述列）
                description_value = ""
                if product_col is not None and product_col < len(row) and row[product_col]:
                    description_value = str(row[product_col]).strip()
                elif counterparty_col is not None and counterparty_col < len(row) and row[counterparty_col]:
                    description_value = str(row[counterparty_col]).strip()
                elif description_col is not None and description_col < len(row) and row[description_col]:
                    description_value = str(row[description_col]).strip()
                
                # 处理日期
                if not date_value:
                    continue
                
                try:
                    if isinstance(date_value, datetime):
                        date_str = date_value.strftime("%Y-%m-%d")
                    else:
                        date_str = str(date_value).strip()
                        # 处理日期时间格式 "2025-11-17 00:00:00" -> "2025-11-17"
                        if ' ' in date_str:
                            date_str = date_str.split(' ')[0]
                except:
                    continue
                
                # 验证日期格式
                if not re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    continue
                
                # 处理金额
                if amount_value is None:
                    continue
                
                try:
                    if isinstance(amount_value, (int, float)):
                        amount = float(amount_value)
                    else:
                        # 尝试从字符串中提取数字（去掉逗号、空格等）
                        amount_str = str(amount_value).replace(',', '').replace('，', '').replace(' ', '').strip()
                        # 去掉可能的货币符号
                        amount_str = re.sub(r'[^\d.-]', '', amount_str)
                        amount = float(amount_str)
                    
                    # 根据交易类型判断收入/支出
                    # 微信账单：交易类型可能是"收入"、"支出"、"中性交易"等
                    is_income = False
                    if type_value:
                        type_str = str(type_value).strip()
                        if '收入' in type_str or 'income' in type_str.lower():
                            is_income = True
                        elif '支出' in type_str or 'expense' in type_str.lower() or '支付' in type_str:
                            is_income = False
                        elif '中性' in type_str or 'neutral' in type_str.lower():
                            # 中性交易（如充值、提现）跳过
                            continue
                    
                    # 如果金额已经是负数，说明是支出
                    if amount < 0:
                        is_income = False
                    elif amount > 0:
                        # 根据交易类型决定
                        if not is_income:
                            amount = -abs(amount)  # 支出转为负数
                        # 如果是收入，保持正数
                    
                except (ValueError, TypeError) as e:
                    continue
                
                # 处理类别和描述
                if not category_value:
                    # 如果没有类别列，根据交易类型或描述推断
                    if type_value and '收入' in str(type_value):
                        category = "收入"
                    else:
                        category = "其他"
                else:
                    category = str(category_value).strip()
                
                if not description_value:
                    description_value = category
                
                # 组合描述：商品 + 交易对方
                description_parts = []
                if product_col is not None and product_col < len(row) and row[product_col]:
                    description_parts.append(str(row[product_col]).strip())
                if counterparty_col is not None and counterparty_col < len(row) and row[counterparty_col]:
                    counterparty = str(row[counterparty_col]).strip()
                    if counterparty and counterparty not in description_parts:
                        description_parts.append(counterparty)
                
                description = ' - '.join(description_parts) if description_parts else description_value
                
                transaction = Transaction(
                    date=date_str,
                    amount=amount,
                    category=category,
                    description=description
                )
                transactions.append(transaction)
        
        except Exception as e:
            raise Exception(f"Excel解析失败：{str(e)}")
        
        return transactions
    
    @staticmethod
    def parse_text(text: str) -> List[Transaction]:
        """从文本解析交易记录（用于AI对话输入）"""
        transactions = []
        # 简单的文本解析逻辑，实际可以使用LLM来解析
        # 格式示例：2024-01-15 餐饮 50 午餐
        pattern = r'(\d{4}-\d{2}-\d{2})\s+(\S+)\s+([\d.]+)\s+(.+)'
        matches = re.findall(pattern, text)
        
        for match in matches:
            date, category, amount_str, description = match
            try:
                amount = float(amount_str)
                # 默认支出为负数
                if amount > 0:
                    amount = -amount
                transaction = Transaction(
                    date=date,
                    amount=amount,
                    category=category,
                    description=description
                )
                transactions.append(transaction)
            except ValueError:
                continue
        
        return transactions


class QueryTool:
    """数据查询工具"""
    
    def __init__(self, storage: DataStorage):
        self.storage = storage
    
    def query_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """查询交易记录"""
        transactions = self.storage.get_transactions(
            start_date=start_date,
            end_date=end_date,
            category=category,
            min_amount=min_amount,
            max_amount=max_amount
        )
        return [t.to_dict() for t in transactions]
    
    def get_monthly_summary(self, month: str) -> Dict[str, Any]:
        """获取月度汇总"""
        transactions = self.storage.get_transactions_by_month(month)
        income = sum(t.amount for t in transactions if t.is_income())
        expense = abs(sum(t.amount for t in transactions if t.is_expense()))
        category_summary = self.storage.get_category_summary(month)
        
        return {
            "month": month,
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "category_summary": category_summary,
            "transaction_count": len(transactions)
        }
    
    def get_category_statistics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取分类统计"""
        transactions = self.storage.get_transactions(start_date=start_date, end_date=end_date)
        category_stats = {}
        
        for t in transactions:
            if t.is_expense():
                category = t.category
                if category not in category_stats:
                    category_stats[category] = {
                        "total": 0,
                        "count": 0,
                        "avg": 0
                    }
                category_stats[category]["total"] += abs(t.amount)
                category_stats[category]["count"] += 1
        
        # 计算平均值
        for category in category_stats:
            if category_stats[category]["count"] > 0:
                category_stats[category]["avg"] = (
                    category_stats[category]["total"] / category_stats[category]["count"]
                )
        
        return category_stats


class AnalysisTool:
    """分析工具"""
    
    def __init__(self, storage: DataStorage):
        self.storage = storage
    
    def calculate_remaining_budget(self, month: str) -> Dict[str, Any]:
        """计算剩余预算"""
        budget = self.storage.get_budget(month)
        if not budget:
            return {"error": f"未设置 {month} 的预算"}
        
        summary = self.storage.get_category_summary(month)
        remaining = {}
        
        # 总预算剩余
        total_expense = self.storage.get_total_expense(month)
        remaining["total"] = budget.total_budget - total_expense
        
        # 分类预算剩余
        remaining["categories"] = {}
        for category, budget_amount in budget.category_budgets.items():
            expense = summary.get(category, 0)
            remaining["categories"][category] = budget_amount - expense
        
        return {
            "month": month,
            "total_budget": budget.total_budget,
            "total_expense": total_expense,
            "remaining": remaining
        }
    
    def get_spending_trend(self, months: int = 3) -> Dict[str, Any]:
        """获取支出趋势"""
        # 获取最近N个月的数据
        from datetime import datetime, timedelta
        trends = []
        
        current = datetime.now()
        for i in range(months):
            month_date = current - timedelta(days=30 * i)
            month_str = month_date.strftime("%Y-%m")
            summary = self.storage.get_category_summary(month_str)
            total_expense = self.storage.get_total_expense(month_str)
            
            trends.append({
                "month": month_str,
                "total_expense": total_expense,
                "categories": summary
            })
        
        return {"trends": trends}
    
    def find_anomalies(self, month: Optional[str] = None) -> List[Dict[str, Any]]:
        """发现异常交易（大额支出、频繁交易等）"""
        transactions = self.storage.get_transactions_by_month(month) if month else self.storage.transactions
        anomalies = []
        
        # 找出大额支出（超过平均值的2倍）
        expenses = [t for t in transactions if t.is_expense()]
        if expenses:
            amounts = [abs(t.amount) for t in expenses]
            avg_amount = sum(amounts) / len(amounts)
            threshold = avg_amount * 2
            
            for t in expenses:
                if abs(t.amount) > threshold:
                    anomalies.append({
                        "type": "large_expense",
                        "transaction": t.to_dict(),
                        "reason": f"金额 {abs(t.amount):.2f} 超过平均值的2倍 ({avg_amount:.2f})"
                    })
        
        return anomalies


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self, storage: DataStorage):
        self.storage = storage
        self.tools: Dict[str, Tool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """注册所有工具"""
        file_parser = FileParserTool()
        query_tool = QueryTool(self.storage)
        analysis_tool = AnalysisTool(self.storage)
        
        # 文件解析工具
        self.tools["parse_csv"] = Tool(
            name="parse_csv",
            description="解析CSV文件，提取交易记录。参数：file_path (文件路径)",
            func=file_parser.parse_csv
        )
        
        self.tools["parse_json"] = Tool(
            name="parse_json",
            description="解析JSON文件，提取交易记录。参数：file_path (文件路径)",
            func=file_parser.parse_json
        )
        
        self.tools["parse_excel"] = Tool(
            name="parse_excel",
            description="解析Excel文件（.xlsx, .xls），提取交易记录。参数：file_path (文件路径)",
            func=file_parser.parse_excel
        )
        
        self.tools["parse_text"] = Tool(
            name="parse_text",
            description="从文本解析交易记录。参数：text (文本内容)",
            func=file_parser.parse_text
        )
        
        # 查询工具
        self.tools["query_transactions"] = Tool(
            name="query_transactions",
            description="查询交易记录。参数：start_date, end_date, category, min_amount, max_amount",
            func=query_tool.query_transactions
        )
        
        self.tools["get_monthly_summary"] = Tool(
            name="get_monthly_summary",
            description="获取月度汇总。参数：month (YYYY-MM格式)",
            func=query_tool.get_monthly_summary
        )
        
        self.tools["get_category_statistics"] = Tool(
            name="get_category_statistics",
            description="获取分类统计。参数：start_date, end_date",
            func=query_tool.get_category_statistics
        )
        
        # 分析工具
        self.tools["calculate_remaining_budget"] = Tool(
            name="calculate_remaining_budget",
            description="计算剩余预算。参数：month (YYYY-MM格式)",
            func=analysis_tool.calculate_remaining_budget
        )
        
        self.tools["get_spending_trend"] = Tool(
            name="get_spending_trend",
            description="获取支出趋势。参数：months (月数，默认3)",
            func=analysis_tool.get_spending_trend
        )
        
        self.tools["find_anomalies"] = Tool(
            name="find_anomalies",
            description="发现异常交易。参数：month (可选，YYYY-MM格式)",
            func=analysis_tool.find_anomalies
        )
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> str:
        """获取所有工具的描述（用于Prompt）"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)

