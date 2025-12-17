# ConverterLearningAgent 使用说明

## 概述

`ConverterLearningAgent` 是专门用于文件转换交互式学习的Agent，能够：
- 自动分析文件结构
- 识别转换问题
- 与用户交互获取指导
- 生成转换规则

## 核心功能

### 1. 从文件学习 (`learn_from_file`)

自动分析文件，尝试生成规则或识别需要交互的问题。

```python
from converter_agent import ConverterLearningAgent
import os

agent = ConverterLearningAgent(api_key=os.getenv("OPENAI_API_KEY"))

result = agent.learn_from_file("微信支付账单流水.xlsx")

if result["status"] == "success":
    print(f"✅ {result['message']}")
    rule = result["rule"]
    # 规则已保存，可以直接使用
elif result["status"] == "need_interaction":
    print("需要用户交互")
    issues = result["issues"]
    structure_info = result["structure_info"]
    # 展示给用户，获取指导
```

### 2. 与用户交互 (`interact_with_user`)

根据用户输入生成规则。

```python
# 用户提供了指导信息
user_input = "表头在第10行，'收/支'列中'收'表示收入，'支'表示支出"

result = agent.interact_with_user(
    file_path="文件.xlsx",
    issues=issues,
    structure_info=structure_info,
    format_info=format_info,
    user_input=user_input
)

if result["status"] == "success":
    rule = result["rule"]
    print(f"✅ 成功生成规则：{rule.rule_id}")
elif result["status"] == "continue":
    questions = result["questions"]
    # 需要继续询问用户
    for q in questions:
        print(f"❓ {q}")
```

### 3. 格式化结构信息 (`format_structure_info`)

将文件结构信息格式化为可读的文本。

```python
formatted = agent.format_structure_info(structure_info)
print(formatted)

# 输出示例：
# 📋 表头位置：第 10 行
# 📊 列名：
#   1. 交易时间
#   2. 收/支金额
#   3. 收/支
#   4. 商品
#   5. 交易对方
# 
# 📝 示例数据（前3行）：
#   第1行：2025-12-15, 9300.0, 支, 二维码收款, 小车百货
#   ...
```

## 工作流程示例

### 场景：首次导入新格式文件

```python
from converter_agent import ConverterLearningAgent
from file_converter import FileConverter
import os

api_key = os.getenv("OPENAI_API_KEY")
agent = ConverterLearningAgent(api_key)

# 1. 尝试学习
result = agent.learn_from_file("新格式账单.xlsx")

if result["status"] == "need_interaction":
    # 2. 展示结构信息
    print(agent.format_structure_info(result["structure_info"]))
    print("\n问题：")
    for issue in result["issues"]:
        print(f"  - {issue}")
    
    # 3. 获取用户输入
    user_input = input("\n请提供指导信息：")
    
    # 4. 生成规则
    rule_result = agent.interact_with_user(
        file_path="新格式账单.xlsx",
        issues=result["issues"],
        structure_info=result["structure_info"],
        format_info=result["format_info"],
        user_input=user_input
    )
    
    if rule_result["status"] == "success":
        print(f"✅ 规则已生成：{rule_result['rule'].rule_id}")
    else:
        # 需要更多信息
        for q in rule_result["questions"]:
            print(f"❓ {q}")
```

## 集成到CoordinatorAgent

可以在 `CoordinatorAgent` 中集成文件转换学习功能：

```python
class CoordinatorAgent:
    def __init__(self, ...):
        # ...
        from converter_agent import ConverterLearningAgent
        self.converter_agent = ConverterLearningAgent(api_key)
    
    def process_file_import(self, file_path: str, user_input: Optional[str] = None):
        """处理文件导入，支持交互式学习"""
        # 尝试学习
        result = self.converter_agent.learn_from_file(file_path, user_input)
        
        if result["status"] == "success":
            # 使用规则提取数据
            from file_converter import FileConverter
            converter = FileConverter(api_key=self.api_key)
            success, transactions, message = converter.convert(file_path, interactive=False)
            return message
        elif result["status"] == "need_interaction":
            # 需要用户交互
            structure_info = result["structure_info"]
            formatted = self.converter_agent.format_structure_info(structure_info)
            
            return f"""需要您的帮助来建立转换规则：

{formatted}

问题：
{chr(10).join(f'- {issue}' for issue in result['issues'])}

请告诉我：
1. 表头在第几行？
2. 如何判断收入/支出？
3. 各列的含义是什么？
"""
```

## 方法说明

### `learn_from_file(file_path, user_input=None)`

分析文件并尝试生成规则。

**返回：**
```python
{
    "status": "success|need_interaction|error",
    "rule": ConversionRule or None,
    "issues": List[str],
    "message": str,
    "structure_info": Dict,  # 如果status是need_interaction
    "format_info": FormatInfo  # 如果status是need_interaction
}
```

### `interact_with_user(file_path, issues, structure_info, format_info, user_input)`

根据用户输入生成规则。

**返回：**
```python
{
    "status": "success|continue",
    "rule": ConversionRule or None,
    "questions": List[str],  # 如果status是continue
    "message": str
}
```

### `format_structure_info(structure_info)`

格式化结构信息为可读文本。

**参数：**
- `structure_info`: 结构信息字典

**返回：**
- 格式化的字符串

## 注意事项

1. **API Key**：需要OpenAI API Key用于LLM调用
2. **文件格式**：当前主要支持Excel格式
3. **规则存储**：规则自动保存到 `data/rules/` 目录
4. **交互流程**：可能需要多轮交互才能生成完整规则

## 未来扩展

- [ ] 支持CSV和JSON格式
- [ ] 规则验证和优化
- [ ] 批量学习多个文件
- [ ] 规则版本管理
- [ ] 规则质量评分

