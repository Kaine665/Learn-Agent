# 文件转换框架使用说明

## 概述

新的文件转换框架实现了智能的、可学习的文件转换系统，支持：
- 自动识别文件格式
- 规则匹配和复用
- 交互式学习新格式
- 规则持久化存储

## 架构

```
FileConverter（主入口）
├── FormatDetector（格式检测）
├── RuleManager（规则管理）
├── DataExtractor（数据提取）
└── InteractiveLearner（交互式学习）
```

## 使用方式

### 1. 基本使用

```python
from file_converter import FileConverter
import os

# 初始化（可选传入API Key用于交互式学习）
api_key = os.getenv("OPENAI_API_KEY")
converter = FileConverter(api_key=api_key)

# 转换文件
success, transactions, message = converter.convert("微信支付账单流水.xlsx")

if success:
    print(f"成功提取 {len(transactions)} 条记录")
else:
    print(f"提取失败：{message}")
```

### 2. 在工具系统中使用

`tools.py` 中的 `FileParserTool.parse_excel()` 已经集成了新框架：

```python
# 自动使用新框架（如果可用）
transactions = FileParserTool.parse_excel("文件.xlsx", api_key=api_key)

# 如果新框架失败，会自动回退到传统方法
```

## 工作流程

### 首次导入新格式

1. **格式检测**：自动识别文件格式和特征
2. **规则查找**：查找匹配的转换规则
3. **自动提取**：尝试自动提取（如果可能）
4. **交互学习**：无法确定时，与用户讨论
5. **规则生成**：生成并保存转换规则

### 再次导入相同格式

1. **格式检测**：识别文件格式
2. **规则匹配**：找到匹配的规则
3. **直接提取**：应用规则提取数据

## 规则存储

规则保存在 `data/rules/` 目录下，每个规则一个JSON文件。

### 规则文件示例

```json
{
  "rule_id": "wechat_xlsx_v1",
  "source_type": "wechat",
  "file_format": "xlsx",
  "format_signatures": [
    "包含'微信支付账单明细'",
    "表头在第10行",
    "有'收/支'列"
  ],
  "structure_mapping": {
    "header_row": {
      "row": 10
    },
    "column_mapping": {
      "date": {
        "patterns": ["交易时间", "时间"]
      },
      "amount": {
        "patterns": ["收/支金额", "金额"]
      },
      "income_expense": {
        "patterns": ["收/支", "收支"]
      }
    }
  },
  "transformation_logic": {
    "is_income": {
      "priority": ["income_expense", "type"]
    }
  },
  "validation_rules": [],
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00",
  "usage_count": 0,
  "success_rate": 1.0
}
```

## 当前状态

### 已实现
- ✅ 格式检测器（FormatDetector）
- ✅ 规则管理器（RuleManager）
- ✅ 数据提取器（DataExtractor）
- ✅ 规则存储和加载
- ✅ 与现有工具系统集成

### 待完善
- ⏳ 交互式学习器（InteractiveLearner）的完整实现
- ⏳ 规则自动生成
- ⏳ 规则验证和优化
- ⏳ CSV和JSON格式的完整支持

## 向后兼容

如果新框架不可用或失败，系统会自动回退到传统的解析方法（`_parse_excel_legacy`），确保向后兼容。

## 扩展

要支持新格式，可以：

1. **手动创建规则**：在 `data/rules/` 目录下创建规则JSON文件
2. **交互式学习**：通过 `InteractiveLearner` 与用户讨论生成规则
3. **代码扩展**：在 `DataExtractor` 中添加新的提取方法

## 注意事项

- 规则文件使用UTF-8编码
- 规则ID应该唯一
- 格式特征签名用于规则匹配，应该准确描述格式特征
- 列映射使用模式匹配，支持多种列名变体

