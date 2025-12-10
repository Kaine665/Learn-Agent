# 实践2：工具集成 Agent

## 目标

在实践1的基础上，学习如何设计和集成工具系统，让 Agent 真正具备"行动能力"。

## 核心概念

### 工具使用（Tool Use）

工具是 Agent 的"外部手臂"，让 Agent 能够：
- 搜索信息（Search）
- 进行计算（Calculator）
- 访问文件系统（File System）
- 调用 API（API Calls）
- 执行代码（Code Execution）

### 工具抽象层

设计一个统一的工具接口：

```python
class Tool:
    name: str           # 工具名称
    description: str     # 工具描述（给 LLM 看的）
    func: callable      # 工具函数
```

### 工具调用流程

1. **工具注册**：将工具注册到 Agent
2. **工具描述**：将工具描述传给 LLM
3. **工具选择**：LLM 根据任务选择工具
4. **工具执行**：Agent 执行选定的工具
5. **结果观察**：将工具结果作为 Observation

## 设计思路

### 1. 工具接口设计

```python
class Tool:
    """工具基类"""
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, *args, **kwargs):
        """执行工具"""
        return self.func(*args, **kwargs)
```

### 2. 工具注册系统

Agent 维护一个工具注册表：

```python
self.tools = {
    "search": Tool(...),
    "calculator": Tool(...),
    ...
}
```

### 3. Prompt 中的工具描述

将工具描述加入 Prompt，让 LLM 知道有哪些工具可用：

```
可用工具：
1. search(query): 搜索信息
2. calculator(expression): 计算数学表达式
3. ...
```

### 4. 工具调用解析

LLM 输出格式：
```
Action: search
Action Input: "Python 教程"
```

Agent 解析后调用对应工具。

## 实现要点

1. **工具抽象**：设计统一的工具接口
2. **工具注册**：实现工具注册机制
3. **工具描述生成**：自动生成工具描述给 LLM
4. **工具调用**：根据 Action 名称调用对应工具
5. **错误处理**：工具调用失败时的处理机制

## 运行示例

```bash
python example.py
```

示例任务：
- "搜索 Python 教程"
- "计算 123 * 456"
- "查询北京的天气"（需要实现天气 API 工具）

## 学习重点

通过这个实践，你将理解：

1. ✅ **工具抽象的重要性**：为什么需要统一的工具接口？
2. ✅ **工具描述的作用**：如何让 LLM 理解工具的能力？
3. ✅ **工具选择机制**：LLM 如何选择合适的工具？
4. ✅ **工具调用流程**：从 Action 到工具执行的完整流程

## 下一步

完成这个实践后，进入 **实践3：Plan-and-Execute Agent**，学习如何让 Agent 执行长任务。

