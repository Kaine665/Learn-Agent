# 实践1.1：Function Calling - 结构化数据返回

## 目标

学习使用 OpenAI 的 Function Calling 功能，让 LLM 直接返回结构化数据，而不是通过正则表达式解析文本。

## 核心概念

### Function Calling vs 正则解析

**实践1（正则解析）的问题：**
- LLM 返回自然语言文本
- 需要手动解析（正则表达式）
- 格式变化会导致解析失败
- 容易出错，不够可靠

**Function Calling 的优势：**
- LLM 直接返回结构化 JSON
- 无需手动解析
- 更可靠，格式固定
- 这是现代 Agent 框架的标准方式

### Function Calling 工作原理

```python
# 1. 定义函数（工具）
functions = [{
    "name": "calculate",
    "description": "计算数学表达式",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "数学表达式"}
        },
        "required": ["expression"]
    }
}]

# 2. LLM 调用时返回结构化数据
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    functions=functions  # ← 告诉 LLM 有哪些函数可用
)

# 3. 直接获取结构化结果
if response.choices[0].message.function_call:
    function_name = response.choices[0].message.function_call.name
    arguments = json.loads(response.choices[0].message.function_call.arguments)
    # arguments 已经是 JSON 对象，无需解析！
```

## 设计思路

### 1. 函数定义

每个工具对应一个函数定义：

```python
{
    "name": "calculate",           # 函数名称
    "description": "计算数学表达式",  # 函数描述（告诉 LLM 这个函数做什么）
    "parameters": {                 # 参数定义（JSON Schema）
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式"
            }
        },
        "required": ["expression"]
    }
}
```

### 2. LLM 调用

```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    functions=functions,           # 提供函数列表
    function_call="auto"           # 让 LLM 自动决定是否调用函数
)
```

### 3. 结果处理

```python
message = response.choices[0].message

if message.function_call:
    # LLM 决定调用函数
    function_name = message.function_call.name
    arguments = json.loads(message.function_call.arguments)
    # 执行函数
    result = execute_function(function_name, arguments)
else:
    # LLM 直接回答
    answer = message.content
```

## 实现要点

1. **函数定义**：如何定义函数 Schema？
2. **函数调用检测**：如何判断 LLM 是否调用了函数？
3. **参数解析**：如何解析函数参数（已经是 JSON）？
4. **函数执行**：如何根据函数名执行对应函数？
5. **结果返回**：如何将函数结果返回给 LLM？

## 运行示例

```bash
python example.py
```

示例任务：
- "计算 123 + 456"
- "搜索 Python 教程"
- "帮我写一首诗"

## 学习重点

通过这个实践，你将理解：

1. ✅ **Function Calling 的优势**：为什么比正则解析更好？
2. ✅ **函数定义**：如何定义函数 Schema？
3. ✅ **结构化返回**：LLM 如何返回结构化数据？
4. ✅ **函数调用流程**：从定义到执行的完整流程
5. ✅ **对比学习**：Function Calling vs 正则解析

## 对比：正则解析 vs Function Calling

| 特性 | 正则解析 | Function Calling |
|------|----------|------------------|
| 可靠性 | 低（格式变化会失败） | 高（格式固定） |
| 实现复杂度 | 中等（需要写正则） | 低（无需解析） |
| LLM 理解 | 需要 Prompt 约束 | 自动理解函数 |
| 错误处理 | 需要手动处理 | 自动处理 |
| 现代性 | 传统方式 | 现代标准 |

## 下一步

完成这个实践后，对比实践1和1.1，理解两种方式的差异，并思考：
- 什么时候用正则解析？
- 什么时候用 Function Calling？
- 实际框架（如 LangChain）是如何实现的？

