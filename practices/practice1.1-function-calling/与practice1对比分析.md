# Practice 1.1 vs Practice 1：ReAct 实现对比分析

## 核心问题

**为什么同样是 ReAct 架构，结果差异这么大？**

从终端输出可以看到：
- **Practice 1**（最简 ReAct）：对于"写全栈安卓软件"任务，迭代了 10 次，逐步输出详细内容
- **Practice 1.1**（Function Calling）：对于同样任务，只迭代了 1 次就结束了，输出很简略

## 关键差异分析

### 差异1：System Prompt 的设计

#### Practice 1（最简 ReAct）

```python
def _build_system_prompt(self) -> str:
    return """你是一个智能助手，能够通过思考和行动来解决问题。

你的工作方式遵循 ReAct 模式：
1. **Thought（思考）**：分析当前情况，思考下一步要做什么
2. **Action（行动）**：决定执行什么行动
3. **Observation（观察）**：观察行动的结果

请严格按照以下格式输出：

Thought: [你的思考过程]
Action: [行动名称，如：calculate, answer, finish]
Action Input: [行动所需的参数，如果没有则写 None]

当任务完成时，使用 Action: finish 来结束。

示例：
用户：计算 10 + 20
Thought: 用户要求计算 10 + 20，这是一个简单的数学计算
Action: calculate
Action Input: 10 + 20
"""
```

**特点：**
- ✅ **严格的格式约束**：要求 LLM 必须输出 `Thought: ... Action: ... Action Input: ...`
- ✅ **明确的示例**：告诉 LLM 如何输出
- ✅ **强制循环**：除非明确 `Action: finish`，否则会继续循环

#### Practice 1.1（Function Calling）

```python
def _build_system_prompt(self) -> str:
    return """你是一个智能助手，能够通过思考和行动来解决问题。

你的工作方式遵循 ReAct 模式：
1. **Thought（思考）**：分析当前情况，思考下一步要做什么
2. **Action（行动）**：决定执行什么行动（通过调用函数）
3. **Observation（观察）**：观察行动的结果

当任务完成时，直接回答用户，不需要调用函数。
"""
```

**特点：**
- ❌ **没有格式约束**：依赖 Function Calling 机制
- ❌ **没有明确示例**：LLM 可能不知道如何逐步输出
- ❌ **完成条件模糊**："直接回答用户" → LLM 可能一次性回答完就结束

---

### 差异2：可用的 Action 类型

#### Practice 1（最简 ReAct）

```python
def _execute_action(self, action: str, action_input: Optional[str]) -> str:
    if action == "finish":
        return "任务完成"
    elif action == "calculate":
        # 计算工具
        ...
    elif action == "answer":
        # 直接回答 ← 关键！
        return f"回答：{action_input}"
    else:
        return f"未知行动：{action}"
```

**关键：有 `answer` action！**

- ✅ LLM 可以使用 `answer` action 来逐步输出内容
- ✅ 每次输出一部分，然后继续循环
- ✅ 可以迭代多次，逐步完成任务

#### Practice 1.1（Function Calling）

```python
def _execute_action(self, action: str, action_input: Dict[str, Any]) -> str:
    if action == "finish":
        return "任务完成"
    
    # 查找工具
    if action not in self.tools:
        return f"错误：未知工具 '{action}'。可用工具：{', '.join(self.tools.keys())}"
    
    tool = self.tools[action]
    # 只有 calculate 和 search 工具
    ...
```

**关键：没有 `answer` action！**

- ❌ 只有 `calculate` 和 `search` 两个工具
- ❌ 没有可以用来"逐步输出内容"的工具
- ❌ LLM 只能一次性回答，然后结束

---

### 差异3：任务完成的判断逻辑

#### Practice 1（最简 ReAct）

```python
# 在 _think 中
# LLM 必须明确输出 Action: finish 才会结束

# 在 run 中
if action == "finish":
    print("✅ 任务完成！")
    break
```

**特点：**
- ✅ LLM 必须**主动**决定何时完成
- ✅ 可以多次使用 `answer` action，直到认为任务完成

#### Practice 1.1（Function Calling）

```python
# 在 _think 中
if message.function_call:
    # LLM 调用了函数
    result = {
        "thought": f"决定调用函数 {function_name}",
        "action": function_name,
        "action_input": arguments,
        "is_function_call": True
    }
else:
    # LLM 直接回答（任务完成）← 关键！
    answer = message.content
    result = {
        "thought": answer,
        "action": "finish",
        "action_input": None,
        "is_function_call": False
    }
```

**特点：**
- ❌ 如果 LLM **不调用函数**，就认为任务完成
- ❌ 对于"写全栈软件"这种任务，LLM 可能认为"我已经回答了"，就不调用函数了
- ❌ 导致只迭代一次就结束

---

## 实际执行对比

### 任务："帮我写一个全栈安卓记账软件"

#### Practice 1（最简 ReAct）的执行流程：

```
[迭代 1]
Thought: 用户需要... → Action: answer → Action Input: 主要功能需求包括...
Observation: 回答：主要功能需求包括...

[迭代 2]
Thought: 已经输出了功能需求，现在应该输出架构设计
→ Action: answer → Action Input: 1. 前端（Android）...
Observation: 回答：1. 前端（Android）...

[迭代 3]
Thought: 已经输出了架构设计，现在应该输出数据结构
→ Action: answer → Action Input: 账单数据结构示例...
Observation: 回答：账单数据结构示例...

... 继续迭代，逐步输出详细内容 ...

[迭代 10]
Thought: 已经输出了所有内容，任务完成
→ Action: finish
✅ 任务完成！
```

**结果：** ✅ 迭代 10 次，输出详细、完整

#### Practice 1.1（Function Calling）的执行流程：

```
[迭代 1]
Thought: 用户需要一个全栈安卓软件...
→ LLM 思考：这个任务需要什么工具？
  - calculate？不需要计算
  - search？不需要搜索
  - 没有合适的工具...
→ LLM 决定：直接回答用户吧
→ 不调用函数，直接输出答案
→ 系统认为：任务完成
✅ 任务完成！
```

**结果：** ❌ 只迭代 1 次，输出简略

---

## 根本原因

### Practice 1.1 的设计缺陷

1. **缺少"输出工具"**：
   - 只有 `calculate` 和 `search` 两个工具
   - 没有可以用来"逐步输出内容"的工具（如 `answer` 或 `write`）

2. **完成条件过于宽松**：
   - "当任务完成时，直接回答用户，不需要调用函数"
   - LLM 可能认为"我已经回答了"，就不继续迭代了

3. **Prompt 不够明确**：
   - 没有告诉 LLM 如何逐步完成任务
   - 没有示例说明如何处理复杂任务

---

## 解决方案

### 方案1：添加"输出工具"

```python
def _register_default_tools(self):
    # ... 现有工具 ...
    
    # 添加输出工具
    def write(content: str) -> str:
        """输出内容给用户"""
        return f"已输出：{content[:100]}..."  # 只返回摘要
    
    self.register_tool("write", write)
```

然后在 System Prompt 中说明：
```python
return """...
你可以使用以下工具：
- calculate: 计算数学表达式
- search: 搜索信息
- write: 输出内容给用户（用于逐步完成任务）

对于复杂任务，请使用 write 工具逐步输出内容，不要一次性回答完。
"""
```

### 方案2：改进完成条件

```python
return """...
当任务完成时，使用 write 工具输出最终总结，然后不再调用任何函数。
不要直接回答用户，始终通过工具来输出内容。
"""
```

### 方案3：添加任务分解指导

```python
return """...
对于复杂任务（如写软件、写文章），请：
1. 先使用 write 输出任务分解
2. 逐步使用 write 输出每个部分
3. 最后使用 write 输出总结
4. 完成时不再调用任何函数
"""
```

---

## 总结

| 维度 | Practice 1 | Practice 1.1 |
|------|-----------|--------------|
| **格式约束** | ✅ 严格格式 | ❌ 无格式约束 |
| **可用 Action** | ✅ calculate, answer, finish | ❌ 只有 calculate, search |
| **完成条件** | ✅ 必须明确 finish | ❌ 不调用函数就完成 |
| **复杂任务处理** | ✅ 可以逐步输出 | ❌ 一次性回答 |
| **迭代次数** | ✅ 多次迭代 | ❌ 通常只迭代1次 |

**核心问题：Practice 1.1 缺少"输出工具"，导致无法逐步完成任务。**

**建议：** 添加 `write` 或 `answer` 工具，并改进 System Prompt，明确告诉 LLM 如何逐步处理复杂任务。
