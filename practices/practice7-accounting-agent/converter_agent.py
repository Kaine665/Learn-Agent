"""
文件转换交互式学习Agent
用于处理文件格式转换的交互式学习
"""

import json
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from file_converter import FormatInfo, ExtractionResult, ConversionRule, FormatDetector, RuleManager
from datetime import datetime


class ConverterLearningAgent:
    """文件转换学习Agent：处理文件格式转换的交互式学习"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        """
        Args:
            api_key: OpenAI API Key
            model: 使用的模型
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.format_detector = FormatDetector()
        self.rule_manager = RuleManager()
    
    def learn_from_file(self, file_path: str, user_input: Optional[str] = None) -> Dict[str, Any]:
        """
        从文件中学习转换规则
        
        Args:
            file_path: 文件路径
            user_input: 用户输入（可选，用于交互）
        
        Returns:
            {
                "status": "success|need_interaction|error",
                "rule": ConversionRule or None,
                "issues": List[str],
                "message": str
            }
        """
        # 1. 检测格式
        format_info = self.format_detector.detect(file_path)
        
        # 2. 查找现有规则
        existing_rule = self.rule_manager.find_rule(format_info)
        if existing_rule:
            return {
                "status": "success",
                "rule": existing_rule,
                "issues": [],
                "message": f"找到匹配规则：{existing_rule.rule_id}"
            }
        
        # 3. 尝试自动识别结构
        structure_info = self._analyze_structure(file_path, format_info)
        
        # 4. 识别问题
        issues = self._identify_issues(structure_info, format_info)
        
        if not issues:
            # 没有问题，可以自动生成规则
            rule = self._generate_rule_auto(format_info, structure_info)
            if rule:
                self.rule_manager.save_rule(rule)
                return {
                    "status": "success",
                    "rule": rule,
                    "issues": [],
                    "message": f"自动生成规则：{rule.rule_id}"
                }
        
        # 5. 需要用户交互
        return {
            "status": "need_interaction",
            "rule": None,
            "issues": issues,
            "message": "需要用户交互来建立转换规则",
            "structure_info": structure_info,
            "format_info": format_info
        }
    
    def interact_with_user(self, file_path: str, issues: List[str], structure_info: Dict, format_info: FormatInfo, user_input: str) -> Dict[str, Any]:
        """
        与用户交互，获取指导并生成规则
        
        Args:
            file_path: 文件路径
            issues: 识别出的问题
            structure_info: 结构信息
            user_input: 用户输入
        
        Returns:
            {
                "status": "success|continue",
                "rule": ConversionRule or None,
                "questions": List[str],  # 需要继续询问的问题
                "message": str
            }
        """
        # 分析用户输入，提取指导信息
        guidance = self._extract_guidance(user_input, issues, structure_info)
        
        # 尝试生成规则
        rule = self._generate_rule_with_guidance(format_info, structure_info, guidance)
        
        if rule:
            # 验证规则
            validation_result = self._validate_rule(file_path, rule)
            
            if validation_result["valid"]:
                self.rule_manager.save_rule(rule)
                return {
                    "status": "success",
                    "rule": rule,
                    "questions": [],
                    "message": f"成功生成规则：{rule.rule_id}"
                }
            else:
                # 规则验证失败，需要更多信息
                return {
                    "status": "continue",
                    "rule": None,
                    "questions": validation_result["questions"],
                    "message": "规则验证失败，需要更多信息"
                }
        else:
            # 无法生成规则，需要更多信息
            remaining_issues = self._identify_remaining_issues(guidance, issues)
            return {
                "status": "continue",
                "rule": None,
                "questions": self._generate_questions(remaining_issues, structure_info),
                "message": "需要更多信息来生成规则"
            }
    
    def _analyze_structure(self, file_path: str, format_info: FormatInfo) -> Dict[str, Any]:
        """
        分析文件结构
        
        Returns:
            {
                "header_row": int or None,
                "column_names": List[str],
                "sample_rows": List[List],
                "metadata_info": Dict
            }
        """
        if format_info.file_type != "xlsx":
            return {}
        
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(file_path)
            ws = wb.active
            
            structure = {
                "header_row": None,
                "column_names": [],
                "sample_rows": [],
                "metadata_info": {}
            }
            
            # 查找表头
            for row_idx in range(1, min(50, ws.max_row + 1)):
                row = [cell.value for cell in ws[row_idx]]
                row_str = ' '.join([str(cell).strip() for cell in row if cell]).lower()
                
                # 检查是否是表头（包含"交易时间"和"金额"）
                if '交易时间' in row_str and ('金额' in row_str or '收/支' in row_str):
                    structure["header_row"] = row_idx
                    structure["column_names"] = [str(cell).strip() if cell else "" for cell in row]
                    break
            
            # 获取示例数据行
            if structure["header_row"]:
                for row_idx in range(structure["header_row"] + 1, min(structure["header_row"] + 6, ws.max_row + 1)):
                    row = [cell.value for cell in ws[row_idx]]
                    if any(row):
                        structure["sample_rows"].append([str(cell).strip() if cell else "" for cell in row])
            
            return structure
        except Exception as e:
            return {"error": str(e)}
    
    def _identify_issues(self, structure_info: Dict, format_info: FormatInfo) -> List[str]:
        """识别问题"""
        issues = []
        
        if "error" in structure_info:
            issues.append(f"结构分析失败：{structure_info['error']}")
            return issues
        
        if structure_info.get("header_row") is None:
            issues.append("无法确定表头位置")
        
        column_names = structure_info.get("column_names", [])
        
        # 检查必要的列
        has_date = any('时间' in col or 'date' in col.lower() for col in column_names)
        has_amount = any('金额' in col or 'amount' in col.lower() for col in column_names)
        has_income_expense = any('收/支' in col or '收支' in col for col in column_names)
        
        if not has_date:
            issues.append("无法找到日期列（交易时间）")
        if not has_amount:
            issues.append("无法找到金额列")
        if not has_income_expense:
            issues.append("无法找到'收/支'列，无法判断收入/支出")
        
        return issues
    
    def _extract_guidance(self, user_input: str, issues: List[str], structure_info: Dict) -> Dict[str, Any]:
        """
        从用户输入中提取指导信息
        
        Returns:
            {
                "header_row": int or None,
                "column_mapping": Dict,
                "income_expense_logic": Dict,
                "other_guidance": Dict
            }
        """
        prompt = f"""用户输入：{user_input}

当前问题：
{chr(10).join(f'- {issue}' for issue in issues)}

文件结构信息：
- 表头行：{structure_info.get('header_row', '未知')}
- 列名：{', '.join(structure_info.get('column_names', []))}

请从用户输入中提取以下指导信息：
1. 表头位置（如果用户提到）
2. 列映射关系（哪一列对应日期、金额、收/支等）
3. 收入/支出判断逻辑（如何判断是收入还是支出）
4. 其他转换规则

请按照以下JSON格式输出：
{{
    "header_row": 行号（如果有）,
    "column_mapping": {{
        "date": "列名或列号",
        "amount": "列名或列号",
        "income_expense": "列名或列号",
        "category": "列名或列号",
        "product": "列名或列号",
        "counterparty": "列名或列号"
    }},
    "income_expense_logic": {{
        "method": "column|description|default",
        "rules": "判断规则描述"
    }},
    "other_guidance": {{}}
}}

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个文件格式转换专家，擅长从用户描述中提取转换规则。"},
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
            print(f"⚠️ 提取指导信息失败：{e}")
        
        return {}
    
    def _generate_rule_auto(self, format_info: FormatInfo, structure_info: Dict) -> Optional[ConversionRule]:
        """自动生成规则"""
        if structure_info.get("header_row") is None:
            return None
        
        column_names = structure_info.get("column_names", [])
        
        # 建立列映射
        column_mapping = {}
        
        for i, col_name in enumerate(column_names):
            col_lower = col_name.lower()
            if '时间' in col_name or 'date' in col_lower or 'time' in col_lower:
                column_mapping["date"] = {"patterns": [col_name], "index": i}
            elif '金额' in col_name or 'amount' in col_lower or 'money' in col_lower:
                column_mapping["amount"] = {"patterns": [col_name], "index": i}
            elif '收/支' in col_name or '收支' in col_name:
                column_mapping["income_expense"] = {"patterns": [col_name], "index": i}
            elif '类型' in col_name or 'type' in col_lower:
                column_mapping["type"] = {"patterns": [col_name], "index": i}
            elif '类别' in col_name or 'category' in col_lower:
                column_mapping["category"] = {"patterns": [col_name], "index": i}
            elif '商品' in col_name or 'product' in col_lower:
                column_mapping["product"] = {"patterns": [col_name], "index": i}
            elif '对方' in col_name or 'counterparty' in col_lower:
                column_mapping["counterparty"] = {"patterns": [col_name], "index": i}
        
        if "date" not in column_mapping or "amount" not in column_mapping:
            return None
        
        # 生成规则ID
        rule_id = f"{format_info.source_type}_{format_info.file_type}_v1"
        
        rule = ConversionRule(
            rule_id=rule_id,
            source_type=format_info.source_type,
            file_format=format_info.file_type,
            format_signatures=format_info.signatures,
            structure_mapping={
                "header_row": {"row": structure_info["header_row"]},
                "column_mapping": column_mapping
            },
            transformation_logic={
                "is_income": {
                    "priority": ["income_expense", "type", "description"]
                }
            },
            validation_rules=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        return rule
    
    def _generate_rule_with_guidance(self, format_info: FormatInfo, structure_info: Dict, guidance: Dict) -> Optional[ConversionRule]:
        """根据用户指导生成规则"""
        column_names = structure_info.get("column_names", [])
        header_row = guidance.get("header_row") or structure_info.get("header_row")
        
        if header_row is None:
            return None
        
        # 建立列映射
        column_mapping = {}
        guidance_mapping = guidance.get("column_mapping", {})
        
        for field, value in guidance_mapping.items():
            if isinstance(value, int):
                # 列号
                if value < len(column_names):
                    column_mapping[field] = {"patterns": [column_names[value]], "index": value}
            elif isinstance(value, str):
                # 列名
                # 查找匹配的列
                for i, col_name in enumerate(column_names):
                    if value in col_name or col_name in value:
                        column_mapping[field] = {"patterns": [col_name], "index": i}
                        break
        
        # 如果指导中没有提供，尝试自动识别
        if "date" not in column_mapping:
            for i, col_name in enumerate(column_names):
                if '时间' in col_name or 'date' in col_name.lower():
                    column_mapping["date"] = {"patterns": [col_name], "index": i}
                    break
        
        if "amount" not in column_mapping:
            for i, col_name in enumerate(column_names):
                if '金额' in col_name or 'amount' in col_name.lower():
                    column_mapping["amount"] = {"patterns": [col_name], "index": i}
                    break
        
        if "date" not in column_mapping or "amount" not in column_mapping:
            return None
        
        # 生成规则
        rule_id = f"{format_info.source_type}_{format_info.file_type}_v1"
        
        income_expense_logic = guidance.get("income_expense_logic", {})
        priority = []
        if "income_expense" in column_mapping:
            priority.append("income_expense")
        if "type" in column_mapping:
            priority.append("type")
        priority.append("description")
        
        rule = ConversionRule(
            rule_id=rule_id,
            source_type=format_info.source_type,
            file_format=format_info.file_type,
            format_signatures=format_info.signatures,
            structure_mapping={
                "header_row": {"row": header_row},
                "column_mapping": column_mapping
            },
            transformation_logic={
                "is_income": {
                    "priority": priority,
                    "method": income_expense_logic.get("method", "column")
                }
            },
            validation_rules=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        return rule
    
    def _validate_rule(self, file_path: str, rule: ConversionRule) -> Dict[str, Any]:
        """验证规则"""
        from file_converter import DataExtractor
        
        extractor = DataExtractor(self.rule_manager)
        result = extractor.extract(file_path, rule)
        
        if result.success and len(result.data) > 0:
            return {
                "valid": True,
                "questions": []
            }
        else:
            return {
                "valid": False,
                "questions": result.issues + result.validation_errors
            }
    
    def _identify_remaining_issues(self, guidance: Dict, original_issues: List[str]) -> List[str]:
        """识别剩余问题"""
        remaining = []
        
        if "header_row" not in guidance:
            if "无法确定表头位置" in original_issues:
                remaining.append("无法确定表头位置")
        
        column_mapping = guidance.get("column_mapping", {})
        if "date" not in column_mapping:
            remaining.append("无法确定日期列")
        if "amount" not in column_mapping:
            remaining.append("无法确定金额列")
        
        return remaining
    
    def _generate_questions(self, issues: List[str], structure_info: Dict) -> List[str]:
        """生成问题"""
        questions = []
        
        column_names = structure_info.get("column_names", [])
        
        if "无法确定表头位置" in issues:
            questions.append(f"表头在第几行？我看到这些列名：{', '.join(column_names)}")
        
        if "无法确定日期列" in issues:
            questions.append("哪一列是日期/交易时间？")
        
        if "无法确定金额列" in issues:
            questions.append("哪一列是金额？")
        
        if "无法找到'收/支'列" in issues:
            questions.append("如何判断收入/支出？有'收/支'列吗？还是需要从其他列判断？")
        
        return questions
    
    def format_structure_info(self, structure_info: Dict) -> str:
        """格式化结构信息，用于展示给用户"""
        lines = []
        
        if structure_info.get("header_row"):
            lines.append(f"📋 表头位置：第 {structure_info['header_row']} 行")
        
        column_names = structure_info.get("column_names", [])
        if column_names:
            lines.append(f"📊 列名：")
            for i, col_name in enumerate(column_names):
                lines.append(f"  {i+1}. {col_name}")
        
        sample_rows = structure_info.get("sample_rows", [])
        if sample_rows:
            lines.append(f"\n📝 示例数据（前{len(sample_rows)}行）：")
            for i, row in enumerate(sample_rows[:3], 1):
                lines.append(f"  第{i}行：{', '.join(str(cell)[:20] for cell in row[:5])}")
        
        return "\n".join(lines)

