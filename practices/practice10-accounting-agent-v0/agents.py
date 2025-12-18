"""
Agent系统：多Agent协作的记账助手
"""

import re
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from abc import ABC, abstractmethod
from storage import DataStorage
from tools import ToolRegistry, FileParserTool
from models import Transaction
from memory import ShortTermMemory, LongTermMemory


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, role: str, expertise: str, api_key: str, model: str = "gpt-4.1"):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    @abstractmethod
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理任务"""
        pass
    
    def _build_prompt(self, task: str, context: Dict[str, Any] = None) -> str:
        """构建Prompt"""
        prompt = f"""你是 {self.name}，角色是 {self.role}，专长是 {self.expertise}。

你的任务是：{task}
"""
        if context:
            prompt += "\n上下文信息：\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += "\n请基于你的专长完成任务。"
        return prompt


class DataEntryAgent(BaseAgent):
    """数据录入Agent：处理对话和文件输入"""
    
    def __init__(self, api_key: str, storage: DataStorage, model: str = "gpt-4.1"):
        super().__init__(
            name="DataEntryAgent",
            role="数据录入专家",
            expertise="从对话和文件中提取交易记录，进行数据清洗和分类",
            api_key=api_key,
            model=model
        )
        self.storage = storage
        self.file_parser = FileParserTool()
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理数据录入任务"""
        # 检查是否是文件路径（必须是有效的非空字符串）
        if context and "file_path" in context:
            file_path = context["file_path"]
            # 确保file_path是有效的文件路径（非None、非空字符串、且看起来像文件路径）
            if file_path and isinstance(file_path, str) and file_path.strip():
                return self._process_file(file_path)
        
        # 否则处理对话输入
        return self._process_conversation(task)
    
    def _process_file(self, file_path: str) -> str:
        """处理文件输入"""
        try:
            file_path_lower = file_path.lower()
            if file_path_lower.endswith('.csv'):
                transactions = self.file_parser.parse_csv(file_path)
            elif file_path_lower.endswith('.json'):
                transactions = self.file_parser.parse_json(file_path)
            elif file_path_lower.endswith('.xlsx') or file_path_lower.endswith('.xls'):
                transactions = self.file_parser.parse_excel(file_path)
            else:
                return f"不支持的文件格式：{file_path}\n支持格式：CSV、JSON、Excel (.xlsx, .xls)"
            
            # 添加到存储
            added_count = self.storage.add_transactions(transactions)
            return f"✅ 成功导入 {added_count} 条交易记录"
        except Exception as e:
            return f"❌ 文件处理失败：{str(e)}"
    
    def _process_conversation(self, user_input: str) -> str:
        """处理对话输入，使用LLM提取交易信息"""
        prompt = f"""用户输入：{user_input}

请从用户输入中提取交易记录信息。用户可能用自然语言描述交易，例如：
- "今天中午吃饭花了50元"
- "1月15日，交通费30元，地铁"
- "收入5000元，工资"

请提取以下信息：
1. 日期（如果没有，使用今天）
2. 金额（正数为收入，负数为支出）
3. 类别（如：餐饮、交通、购物、收入等）
4. 描述

请按照以下JSON格式输出：
{{
    "date": "YYYY-MM-DD",
    "amount": 金额（负数表示支出，正数表示收入）,
    "category": "类别",
    "description": "描述"
}}

如果有多条交易，请输出JSON数组。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个数据提取专家，擅长从自然语言中提取结构化数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30
            )
        except Exception as e:
            return f"❌ API调用失败：{str(e)}\n请检查网络连接或稍后重试。"
        
        result = response.choices[0].message.content
        
        # 尝试解析JSON
        try:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # 处理单条或多条记录
                if isinstance(data, list):
                    transactions = [Transaction.from_dict(item) for item in data]
                else:
                    transactions = [Transaction.from_dict(data)]
                
                # 添加到存储
                added_count = self.storage.add_transactions(transactions)
                return f"✅ 成功添加 {added_count} 条交易记录\n\n提取的信息：\n{json.dumps([t.to_dict() for t in transactions], ensure_ascii=False, indent=2)}"
            else:
                return f"⚠️ 无法提取结构化数据，请检查输入格式。\nLLM输出：{result}"
        except Exception as e:
            return f"❌ 数据处理失败：{str(e)}\nLLM输出：{result}"


class AnalystAgent(BaseAgent):
    """分析Agent：AI洞察分析花销去向"""
    
    def __init__(self, api_key: str, storage: DataStorage, tool_registry: ToolRegistry, model: str = "gpt-4.1"):
        super().__init__(
            name="AnalystAgent",
            role="财务分析专家",
            expertise="分析花销模式、识别趋势、提供财务洞察和建议",
            api_key=api_key,
            model=model
        )
        self.storage = storage
        self.tool_registry = tool_registry
    
    def _identify_analysis_needs(self, task: str) -> Dict[str, Any]:
        """
        识别用户的分析需求
        
        返回：
        {
            "needs": ["simple_query", "category_analysis", "trend_analysis", "budget_analysis", "comprehensive"],
            "focus": "主要关注点",
            "detail_level": "brief|normal|detailed"
        }
        """
        prompt = f"""用户查询：{task}

请分析用户想要什么类型的财务分析。分析需求类型包括：
1. "simple_query" - 简单查询（如"花了多少钱"、"还剩多少预算"、"收入多少"）
2. "category_analysis" - 分类分析（如"餐饮占比"、"哪个类别最多"、"花销去向"）
3. "trend_analysis" - 趋势分析（如"支出趋势"、"对比上个月"、"变化情况"）
4. "budget_analysis" - 预算分析（如"预算使用情况"、"还能花多少"、"预算剩余"）
5. "anomaly_detection" - 异常检测（如"大额支出"、"异常交易"、"不合理消费"）
6. "optimization_suggestion" - 优化建议（如"如何节省"、"省钱建议"、"优化建议"）
7. "comprehensive" - 综合分析（如"全面分析"、"详细分析"、"完整报告"）

请按照以下JSON格式输出：
{{
    "needs": ["需求类型列表"],
    "focus": "主要关注点（一句话描述）",
    "detail_level": "brief|normal|detailed"
}}

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个意图识别专家，擅长分析用户需求。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=15
            )
            
            result = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"⚠️ 分析需求识别失败：{e}")
        
        # 默认返回
        return {
            "needs": ["comprehensive"],
            "focus": "综合分析",
            "detail_level": "normal"
        }
    
    def _gather_data(self, month: Optional[str], analysis_needs: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据分析需求获取数据
        
        Args:
            month: 月份（YYYY-MM格式）
            analysis_needs: 分析需求
        
        Returns:
            包含所需数据的字典
        """
        needs = analysis_needs.get("needs", [])
        data = {}
        
        # 基础数据（总是需要）
        if month:
            summary = self.tool_registry.get_tool("get_monthly_summary").execute(month)
            data["summary"] = summary
        else:
            # 总体统计
            total_income = self.storage.get_total_income()
            total_expense = self.storage.get_total_expense()
            data["summary"] = {
                "total_income": total_income,
                "total_expense": total_expense,
                "balance": total_income - total_expense,
                "transaction_count": len(self.storage.transactions)
            }
        
        # 根据需求获取特定数据
        if any(need in needs for need in ["category_analysis", "comprehensive"]):
            category_stats = self.tool_registry.get_tool("get_category_statistics").execute()
            data["category_statistics"] = category_stats
            
            if month:
                category_summary = self.storage.get_category_summary(month)
                data["summary"]["category_summary"] = category_summary
            
            # 🔥 获取详细交易记录（包含description），用于从描述中提取实际信息
            # category字段是原始数据，可能不准确（如都是"其他"），需要从description中提取真实信息
            if month:
                transactions = self.storage.get_transactions_by_month(month)
            else:
                transactions = self.storage.transactions
            
            # 获取支出记录，包含完整的description信息
            expense_transactions = [t.to_dict() for t in transactions if t.is_expense()]
            # 限制数量避免数据过大，但保留足够的信息用于分析
            data["transaction_details"] = expense_transactions[:200]  # 最多200条
        
        if any(need in needs for need in ["trend_analysis", "comprehensive"]):
            trends = self.tool_registry.get_tool("get_spending_trend").execute(months=3)
            data["trends"] = trends
        
        if any(need in needs for need in ["budget_analysis", "comprehensive"]):
            if month:
                remaining_budget = self.tool_registry.get_tool("calculate_remaining_budget").execute(month)
                data["budget"] = remaining_budget
        
        if any(need in needs for need in ["anomaly_detection", "comprehensive"]):
            anomalies = self.tool_registry.get_tool("find_anomalies").execute(month=month)
            data["anomalies"] = anomalies
        
        return data
    
    def _generate_analysis(self, task: str, analysis_needs: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        根据分析需求动态生成分析内容
        
        Args:
            task: 用户查询
            analysis_needs: 分析需求
            data: 数据字典
        """
        needs = analysis_needs.get("needs", [])
        focus = analysis_needs.get("focus", "综合分析")
        detail_level = analysis_needs.get("detail_level", "normal")
        
        # 构建分析指导
        analysis_guide = []
        
        if "simple_query" in needs:
            analysis_guide.append("- 直接、简洁地回答用户的问题，不需要展开分析")
        
        if "category_analysis" in needs:
            analysis_guide.append("- 重点分析分类占比和类别分布")
            analysis_guide.append("- 指出主要支出类别和占比情况")
            # 🔥 重要：从description中提取实际信息，不要只依赖category字段
            analysis_guide.append("- category字段是原始数据，可能不准确（如都是'其他'）")
            analysis_guide.append("- 必须从transaction_details中的description字段提取实际的花销信息")
            analysis_guide.append("- description字段包含：收款方、商品名称、交易对方、交易类型等详细信息")
            analysis_guide.append("- 根据description的实际内容，重新分类并分析花销去向")
            analysis_guide.append("- 可以按收款方、商品类型、交易类型、交易对方等进行分类汇总")
        
        if "trend_analysis" in needs:
            analysis_guide.append("- 分析支出趋势和变化情况")
            analysis_guide.append("- 对比历史数据，指出变化趋势")
        
        if "budget_analysis" in needs:
            analysis_guide.append("- 分析预算使用情况")
            analysis_guide.append("- 计算剩余预算和可花销空间")
        
        if "anomaly_detection" in needs:
            analysis_guide.append("- 识别异常交易和大额支出")
            analysis_guide.append("- 指出不合理的消费模式")
        
        if "optimization_suggestion" in needs:
            analysis_guide.append("- 提供优化建议和节省开支的方法")
        
        if "comprehensive" in needs:
            analysis_guide.append("- 提供全面的财务分析报告")
            analysis_guide.append("- 包括花销去向、趋势、异常、建议等各个方面")
        
        # 根据详细程度调整
        if detail_level == "brief":
            analysis_guide.append("- 回答要简洁，只提供关键信息")
        elif detail_level == "detailed":
            analysis_guide.append("- 回答要详细，提供深入的分析和洞察")
        
        prompt = f"""作为财务分析专家，请根据用户的具体问题提供分析。

用户问题：{task}
主要关注点：{focus}
详细程度：{detail_level}

分析指导：
{chr(10).join(analysis_guide)}

可用数据：
{json.dumps(data, ensure_ascii=False, indent=2)}

⚠️ 重要说明：
1. category字段是原始数据，可能不准确或不完整（如都是"其他"）
2. 必须从transaction_details中的description字段提取实际的花销信息
3. description字段包含真实信息：收款方、商品名称、交易对方、交易类型等
4. 根据description的实际内容，重新分类并分析花销去向
5. 如果用户问"花在了什么地方"或"分别花在"，要从description中提取收款方、商品等信息进行分类

请根据用户问题的具体需求，提供针对性的分析：
- 如果用户问简单问题（如"花了多少钱"、"还剩多少预算"），直接回答数字，简洁明了
- 如果用户问分类问题或"花在了什么地方"，必须从description中提取信息，重新分类分析
- 如果用户问趋势问题，重点分析趋势变化和对比
- 如果用户问预算问题，重点分析预算使用和剩余情况
- 如果用户要求全面分析，才提供完整的分析报告

请用清晰、专业的中文回答，只回答用户关心的内容，不要提供无关信息。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的财务分析专家，擅长根据用户需求提供针对性的财务分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 分析失败：{str(e)}\n请检查网络连接或稍后重试。"
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        处理分析任务（方案3：分层分析）
        
        流程：
        1. 识别分析需求
        2. 根据需求获取数据
        3. 动态生成分析
        """
        month = context.get("month") if context else None
        
        # 第一步：识别分析需求
        print("🔍 识别分析需求...")
        analysis_needs = self._identify_analysis_needs(task)
        print(f"📌 分析需求：{analysis_needs.get('needs', [])}")
        print(f"📌 关注点：{analysis_needs.get('focus', '')}")
        print(f"📌 详细程度：{analysis_needs.get('detail_level', 'normal')}\n")
        
        # 第二步：根据需求获取数据
        print("📊 获取数据...")
        data = self._gather_data(month, analysis_needs)
        print(f"✅ 已获取 {len(data)} 类数据\n")
        
        # 第三步：动态生成分析
        print("💡 生成分析...")
        result = self._generate_analysis(task, analysis_needs, data)
        
        return result


class ReporterAgent(BaseAgent):
    """报告Agent：生成报告和展示历史流水"""
    
    def __init__(self, api_key: str, storage: DataStorage, tool_registry: ToolRegistry, model: str = "gpt-4.1"):
        super().__init__(
            name="ReporterAgent",
            role="报告生成专家",
            expertise="生成财务报告、格式化展示历史流水、创建可视化报告",
            api_key=api_key,
            model=model
        )
        self.storage = storage
        self.tool_registry = tool_registry
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理报告生成任务 - 使用LLM理解查询意图"""
        # 使用 LLM 理解用户真正想要什么
        query_type = self._understand_query_intent(task)
        
        if query_type == "statistics":
            # 统计查询：最早日期、总数、总金额等
            return self._handle_statistics_query(task, context)
        elif query_type == "display":
            # 展示查询：显示交易记录列表
            return self._handle_display_query(context)
        else:
            # 默认展示
            return self._handle_display_query(context)
    
    def _understand_query_intent(self, task: str) -> str:
        """使用 LLM 理解查询意图"""
        prompt = f"""用户查询：{task}

请判断用户想要：
1. 统计查询（如：最早日期、最晚日期、总数、总金额、平均值等）-> 返回 "statistics"
2. 展示查询（如：显示交易记录、查看流水、列出交易等）-> 返回 "display"

只返回一个词：statistics 或 display
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个查询意图理解专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            result = response.choices[0].message.content.strip().lower()
            # 确保返回的是 statistics 或 display
            if "statistic" in result:
                return "statistics"
            elif "display" in result or "show" in result or "list" in result:
                return "display"
            else:
                # 默认返回 display
                return "display"
        except Exception as e:
            print(f"⚠️ 查询意图理解失败：{e}")
            # 默认返回 display
            return "display"
    
    def _handle_statistics_query(self, task: str, context: Dict[str, Any]) -> str:
        """处理统计查询"""
        # 获取数据
        transactions = self._get_transactions_from_context(context)
        
        if not transactions:
            return "📊 未找到符合条件的交易记录"
        
        # 计算基本统计信息
        dates = [t.date for t in transactions]
        amounts = [t.amount for t in transactions]
        income = sum([a for a in amounts if a > 0])
        expense = abs(sum([a for a in amounts if a < 0]))
        
        # 使用 LLM 理解具体要统计什么并回答
        prompt = f"""用户查询：{task}

交易记录统计信息：
- 交易数量：{len(transactions)} 条
- 最早日期：{min(dates)}
- 最晚日期：{max(dates)}
- 总收入：{income:.2f} 元
- 总支出：{expense:.2f} 元
- 结余：{income - expense:.2f} 元

请根据用户查询，直接回答用户的问题。要求：
1. 简洁明了，直接回答
2. 如果问"最早一天"或"最早日期"，回答：最早的一天是 {min(dates)}
3. 如果问"最晚一天"或"最晚日期"，回答：最晚的一天是 {max(dates)}
4. 如果问"总共多少笔"或"多少条记录"，回答：共有 {len(transactions)} 笔交易记录
5. 如果问"总共花了多少钱"或"总支出"，回答：总支出 {expense:.2f} 元
6. 如果问"总收入"，回答：总收入 {income:.2f} 元
7. 如果问"结余"或"余额"，回答：结余 {income - expense:.2f} 元

请直接回答，不要添加多余的解释。
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个财务数据查询专家，能够根据用户查询直接回答统计问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # 如果LLM失败，使用简单的关键词匹配作为后备
            task_lower = task.lower()
            if "最早" in task_lower or "最早一天" in task_lower:
                return f"最早的一天是 {min(dates)}"
            elif "最晚" in task_lower or "最晚一天" in task_lower:
                return f"最晚的一天是 {max(dates)}"
            elif "总共" in task_lower and ("笔" in task_lower or "条" in task_lower):
                return f"共有 {len(transactions)} 笔交易记录"
            elif "总支出" in task_lower or "花了" in task_lower:
                return f"总支出 {expense:.2f} 元"
            elif "总收入" in task_lower:
                return f"总收入 {income:.2f} 元"
            else:
                return f"共有 {len(transactions)} 笔交易记录，总支出 {expense:.2f} 元，总收入 {income:.2f} 元"
    
    def _handle_display_query(self, context: Dict[str, Any]) -> str:
        """处理展示查询（保持原有逻辑）"""
        transactions = self._get_transactions_from_context(context)
        
        if not transactions:
            return "📊 未找到符合条件的交易记录"
        
        # 格式化展示
        report = self._format_transactions(transactions)
        
        # 添加统计信息（如果有月份信息）
        month = context.get("month") if context else None
        if month:
            summary = self.tool_registry.get_tool("get_monthly_summary").execute(month)
            report += f"\n\n📈 月度统计：\n"
            report += f"- 收入：{summary['income']:.2f} 元\n"
            report += f"- 支出：{summary['expense']:.2f} 元\n"
            report += f"- 结余：{summary['balance']:.2f} 元\n"
            report += f"- 交易笔数：{summary['transaction_count']} 笔\n"
        
        return report
    
    def _get_transactions_from_context(self, context: Dict[str, Any]) -> List[Transaction]:
        """从context中获取交易记录"""
        start_date = context.get("start_date") if context else None
        end_date = context.get("end_date") if context else None
        category = context.get("category") if context else None
        month = context.get("month") if context else None
        
        if month:
            return self.storage.get_transactions_by_month(month)
        else:
            return self.storage.get_transactions(
                start_date=start_date,
                end_date=end_date,
                category=category
            )
    
    def _format_transactions(self, transactions: List[Transaction]) -> str:
        """格式化交易记录"""
        report = "📋 交易记录：\n\n"
        report += f"{'日期':<12} {'类别':<10} {'金额':>10} {'描述':<30}\n"
        report += "-" * 70 + "\n"
        
        for t in transactions[:50]:  # 限制显示前50条
            amount_str = f"{t.amount:+.2f}"
            report += f"{t.date:<12} {t.category:<10} {amount_str:>10} {t.description:<30}\n"
        
        if len(transactions) > 50:
            report += f"\n... 还有 {len(transactions) - 50} 条记录未显示\n"
        
        return report


class CoordinatorAgent:
    """协调者Agent：管理所有Agent，处理用户请求"""
    
    def __init__(self, api_key: str, storage: DataStorage, model: str = "gpt-4.1"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.storage = storage
        self.tool_registry = ToolRegistry(storage)
        
        # 记忆系统
        self.stm = ShortTermMemory(max_turns=20)
        self.ltm = LongTermMemory()
        
        # 创建各个Agent
        self.data_entry_agent = DataEntryAgent(api_key, storage, model)
        self.analyst_agent = AnalystAgent(api_key, storage, self.tool_registry, model)
        self.reporter_agent = ReporterAgent(api_key, storage, self.tool_registry, model)
        
        self.agents = {
            "data_entry": self.data_entry_agent,
            "analyst": self.analyst_agent,
            "reporter": self.reporter_agent
        }
    
    def _classify_intent(self, user_input: str) -> Dict[str, Any]:
        """分类用户意图"""
        from datetime import datetime
        current_date = datetime.now()
        current_month = current_date.strftime("%Y-%m")
        current_year = current_date.year
        
        prompt = f"""用户输入：{user_input}
当前日期：{current_date.strftime("%Y-%m-%d")}
当前月份：{current_month}

请分析用户意图，判断用户想要：
1. 录入数据（添加交易记录、导入文件）
2. 查看流水（查询历史记录、展示交易）
3. 分析洞察（分析花销、趋势分析、预算分析）

时间处理规则：
- "这个月"、"本月"、"当前月" -> 使用 {current_month}
- "上个月" -> 使用上一个月（{current_month}的前一个月）
- "X月"（如"1月"）-> 使用 {current_year}-0X 格式
- "X月份" -> 同上

请按照以下JSON格式输出：
{{
    "intent": "data_entry|view|analysis",
    "parameters": {{
        "month": "YYYY-MM" (如果有时间信息，否则不包含),
        "category": "类别" (如果有，否则不包含),
        "start_date": "YYYY-MM-DD" (如果有，否则不包含),
        "end_date": "YYYY-MM-DD" (如果有，否则不包含)
    }}
}}

重要：只包含用户明确提到的参数，不要包含空值或默认值。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个意图识别专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30
            )
            
            result = response.choices[0].message.content
            
            # 解析JSON
            try:
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    intent_data = json.loads(json_match.group(0))
                    # 清理参数：移除空值
                    if "parameters" in intent_data:
                        parameters = intent_data["parameters"]
                        # 移除空字符串、None值
                        parameters = {k: v for k, v in parameters.items() 
                                    if v and v != "" and v is not None}
                        intent_data["parameters"] = parameters
                    return intent_data
            except Exception as e:
                print(f"⚠️ 意图识别解析失败：{e}")
        
        except Exception as e:
            print(f"⚠️ 意图识别请求失败：{e}")
            # 简单的关键词匹配作为后备方案
            user_lower = user_input.lower()
            from datetime import datetime
            
            # 提取月份信息
            parameters = {}
            current_month = datetime.now().strftime("%Y-%m")
            
            # 检查是否提到"这个月"、"本月"、"当前月"
            if any(word in user_lower for word in ["这个月", "本月", "当前月", "这个月"]):
                parameters["month"] = current_month
            
            if any(word in user_lower for word in ["添加", "录入", "记录", "花了", "收入"]):
                return {"intent": "data_entry", "parameters": parameters}
            elif any(word in user_lower for word in ["分析", "花销", "预算", "还能花", "还剩"]):
                return {"intent": "analysis", "parameters": parameters}
            else:
                return {"intent": "view", "parameters": parameters}
        
        # 默认处理
        return {"intent": "view", "parameters": {}}
    
    def process(self, user_input: str, file_path: Optional[str] = None) -> str:
        """处理用户请求"""
        print(f"\n{'='*60}")
        print(f"用户输入：{user_input}")
        if file_path:
            print(f"文件路径：{file_path}")
        print(f"{'='*60}\n")
        
        # 添加到短期记忆
        self.stm.add("user", user_input)
        
        # 如果有文件路径，直接使用数据录入Agent
        if file_path:
            context = {"file_path": file_path}
            result = self.data_entry_agent.process("导入文件", context)
            self.stm.add("assistant", result)
            print(result)
            return result
        
        # 检查长期记忆中的缓存
        cache_key = f"{user_input[:50]}"  # 使用输入的前50个字符作为key
        cached_result = self.ltm.get_analysis_cache(cache_key)
        if cached_result and "分析" in user_input.lower():
            print("💾 使用缓存的分析结果")
            self.stm.add("assistant", cached_result)
            print(cached_result)
            return cached_result
        
        # 分类意图
        try:
            intent_result = self._classify_intent(user_input)
        except Exception as e:
            # 如果分类失败，使用后备方案
            user_lower = user_input.lower()
            if any(word in user_lower for word in ["添加", "录入", "记录", "花了", "收入"]):
                intent_result = {"intent": "data_entry", "parameters": {}}
            elif any(word in user_lower for word in ["分析", "花销", "预算", "还能花", "还剩"]):
                intent_result = {"intent": "analysis", "parameters": {}}
            else:
                intent_result = {"intent": "view", "parameters": {}}
        
        intent = intent_result.get("intent", "view")
        parameters = intent_result.get("parameters", {})
        
        print(f"📌 识别意图：{intent}")
        print(f"📌 参数：{parameters}\n")
        
        # 根据意图路由到相应的Agent
        try:
            if intent == "data_entry":
                result = self.data_entry_agent.process(user_input, parameters)
            elif intent == "analysis":
                result = self.analyst_agent.process(user_input, parameters)
                # 缓存分析结果
                self.ltm.save_analysis_cache(cache_key, result)
            else:  # view
                result = self.reporter_agent.process(user_input, parameters)
        except Exception as e:
            result = f"❌ 处理请求时出错：{str(e)}\n请检查网络连接或稍后重试。"
            print(result)
        
        # 保存到记忆
        self.stm.add("assistant", result)
        self.ltm.save_query_history(user_input, result)
        
        print(result)
        return result

