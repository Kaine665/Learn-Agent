"""
文件转换Agent
只支持硬编码快速通道和规则库匹配
"""

from typing import Optional, Callable
from file_converter import FormatInfo, ConversionRule, FormatDetector, RuleManager


class ConverterAgent:
    """文件转换Agent：只支持硬编码和规则匹配"""
    
    def __init__(self, rules_dir: str = "data/rules"):
        """
        Args:
            rules_dir: 规则存储目录
        """
        self.format_detector = FormatDetector()
        self.rule_manager = RuleManager(rules_dir)
        
        # 快速通道：常见格式的硬编码转换器
        # 格式：{format_key: (detector_func, converter_func)}
        # detector_func: 检测函数，返回 True/False 表示是否匹配
        # converter_func: 转换函数，返回 ConversionRule
        self.quick_routes = {
            # 示例：微信支付账单
            # "wechat_pay": (self._detect_wechat_pay, self._convert_wechat_pay_quick),
            # 示例：支付宝账单
            # "alipay": (self._detect_alipay, self._convert_alipay_quick),
            # 示例：银行账单
            # "bank_statement": (self._detect_bank_statement, self._convert_bank_statement_quick),
            # TODO: 在这里添加更多快速通道
        }
    
    def find_rule(self, file_path: str) -> Optional[ConversionRule]:
        """
        查找转换规则（只支持硬编码和规则库匹配）
        
        Args:
            file_path: 文件路径
        
        Returns:
            ConversionRule 对象，如果找不到则返回 None
        """
        # 1. 快速通道：先尝试硬编码的常见格式（性能最优）
        quick_rule = self._try_quick_route(file_path)
        if quick_rule:
            return quick_rule
        
        # 2. 检测格式
        format_info = self.format_detector.detect(file_path)
        
        # 3. 查找规则库
        rule = self.rule_manager.find_rule(format_info)
        if rule:
            return rule
        
        # 4. 找不到规则，打印失败信息
        print(f"❌ 文件解析失败：未找到匹配的转换规则")
        print(f"   文件路径：{file_path}")
        print(f"   文件类型：{format_info.file_type}")
        print(f"   数据源类型：{format_info.source_type}")
        print(f"   格式特征：{', '.join(format_info.signatures)}")
        return None
    
    # ==================== 快速通道相关方法 ====================
    
    def _try_quick_route(self, file_path: str) -> Optional[ConversionRule]:
        """
        尝试快速通道：检查是否有硬编码的转换器可以处理
        
        Args:
            file_path: 文件路径
        
        Returns:
            如果匹配快速通道，返回 ConversionRule；否则返回 None
        """
        for route_name, (detector_func, converter_func) in self.quick_routes.items():
            try:
                # 检测是否匹配该快速通道
                if detector_func(file_path):
                    # 使用快速转换器生成规则
                    rule = converter_func(file_path)
                    if rule:
                        # 保存规则到规则库（以便后续快速查找）
                        self.rule_manager.save_rule(rule)
                        return rule
            except Exception as e:
                # 快速通道失败，继续尝试其他方法
                print(f"⚠️ 快速通道 {route_name} 处理失败：{e}")
                continue
        
        return None
    
    def register_quick_route(
        self, 
        route_name: str, 
        detector_func: Callable[[str], bool], 
        converter_func: Callable[[str], Optional[ConversionRule]]
    ):
        """
        注册快速通道
        
        Args:
            route_name: 路由名称（如 "wechat_pay"）
            detector_func: 检测函数，接收 file_path，返回 True/False
            converter_func: 转换函数，接收 file_path，返回 ConversionRule
        """
        self.quick_routes[route_name] = (detector_func, converter_func)
    
    # ==================== 快速通道实现模板（供参考） ====================
    
    def _detect_wechat_pay(self, file_path: str) -> bool:
        """
        检测是否为微信支付账单
        
        TODO: 实现你的检测逻辑
        例如：检查文件名、文件内容特征等
        
        Args:
            file_path: 文件路径
        
        Returns:
            True 如果是微信支付账单，False 否则
        """
        # TODO: 实现检测逻辑
        # 示例：
        # import os
        # filename = os.path.basename(file_path).lower()
        # if '微信' in filename or 'wechat' in filename:
        #     return True
        # 
        # # 或者检查文件内容特征
        # # ...
        return False
    
    def _convert_wechat_pay_quick(self, file_path: str) -> Optional[ConversionRule]:
        """
        快速转换微信支付账单
        
        TODO: 实现你的转换逻辑
        直接硬编码转换规则，无需LLM调用
        
        Args:
            file_path: 文件路径
        
        Returns:
            ConversionRule 对象，如果转换失败返回 None
        """
        # TODO: 实现转换逻辑
        # 示例：
        # from file_converter import ConversionRule
        # from datetime import datetime
        # 
        # # 硬编码的转换规则
        # rule = ConversionRule(
        #     rule_id="wechat_pay_xlsx_v1",
        #     source_type="wechat_pay",
        #     file_format="xlsx",
        #     format_signatures=["微信支付", "账单"],
        #     structure_mapping={
        #         "header_row": {"row": 17},  # 微信支付表头在第17行
        #         "column_mapping": {
        #             "date": {"patterns": ["交易时间"], "index": 0},
        #             "amount": {"patterns": ["金额"], "index": 5},
        #             # ... 更多列映射
        #         }
        #     },
        #     transformation_logic={
        #         "is_income": {
        #             "priority": ["income_expense", "type", "description"]
        #         }
        #     },
        #     validation_rules=[],
        #     created_at=datetime.now().isoformat(),
        #     updated_at=datetime.now().isoformat()
        # )
        # 
        # return rule
        return None
    
    def _detect_alipay(self, file_path: str) -> bool:
        """
        检测是否为支付宝账单
        
        TODO: 实现你的检测逻辑
        """
        return False
    
    def _convert_alipay_quick(self, file_path: str) -> Optional[ConversionRule]:
        """
        快速转换支付宝账单
        
        TODO: 实现你的转换逻辑
        """
        return None
    
    def _detect_bank_statement(self, file_path: str) -> bool:
        """
        检测是否为银行账单
        
        TODO: 实现你的检测逻辑
        """
        return False
    
    def _convert_bank_statement_quick(self, file_path: str) -> Optional[ConversionRule]:
        """
        快速转换银行账单
        
        TODO: 实现你的转换逻辑
        """
        return None
    
    # TODO: 在这里添加更多快速通道的检测和转换方法
