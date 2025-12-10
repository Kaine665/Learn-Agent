# 实践 1：最简 ReAct Agent

## 目标

通过实现一个最简化的 ReAct Agent，理解 **Thought-Action-Observation** 循环的核心机制。

## 核心概念

### ReAct = Reasoning + Acting

ReAct 是现代 Agent 的基础范式，它将推理（Reasoning）和行动（Acting）结合在一个循环中：

```
Thought → Action → Observation → Thought → Action → ...
```

### 为什么需要 ReAct？

1. **分离思考与行动**：让 Agent 先思考再行动，而不是盲目执行
2. **观察反馈**：通过 Observation 获取环境反馈，调整下一步策略
3. **自主决策**：Agent 可以根据观察结果自主决定下一步行动

## 设计思路

### 1. Agent 核心循环

```python
while not finished:
    # 1. Thought: Agent 思考下一步要做什么
    thought = agent.think(observation)

    # 2. Action: Agent 决定执行什么行动
    action = agent.decide_action(thought)

    # 3. Observation: 执行行动并观察结果
    observation = agent.execute(action)

    # 4. 判断是否完成
    if agent.is_finished(observation):
        break
```

### 2. Prompt 设计

Agent 的 Prompt 需要明确告诉 LLM：

- 你是谁（角色）
- 你要如何思考（输出 Thought）
- 你要如何行动（输出 Action）
- 如何理解观察结果（Observation）

### 3. 输出格式约束

使用结构化输出格式，让 LLM 按照固定格式输出：

```
Thought: [思考内容]
Action: [行动名称]
Action Input: [行动参数]
```

## 实现要点

1. **LLM 调用**：使用 OpenAI API（或其他 LLM）进行推理
2. **格式解析**：解析 LLM 输出的 Thought/Action 格式
3. **循环控制**：控制循环次数，避免无限循环
4. **终止条件**：判断何时任务完成

## 运行示例

```bash
python example.py
```

示例任务：

- "帮我计算 123 + 456"
- "查询北京的天气"
- "帮我写一首关于春天的诗"

## 学习重点

通过这个实践，你将理解：

1. ✅ **ReAct 循环的本质**：为什么需要 Thought-Action-Observation？
2. ✅ **LLM 在 Agent 中的作用**：LLM 是"大脑"，负责推理和决策
3. ✅ **格式约束的重要性**：如何让 LLM 按照固定格式输出？
4. ✅ **循环控制**：如何避免 Agent 陷入死循环？

## 下一步

完成这个实践后，进入 **实践 2：工具集成 Agent**，学习如何让 Agent 真正"行动"起来。
