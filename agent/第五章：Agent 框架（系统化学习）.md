# 第五章：Agent 框架（系统化学习）

## 本阶段目标

- 理解四大主流 Agent 框架的核心思想、设计模式与工程价值
- 能够用统一的框架分析不同 Agent 体系
- 能够从这些思想中抽象出你未来自己的 Agent 系统
- 能够做基于框架的快速实验与验证

---

## 学习结构总览

```
第五阶段：Agent 框架
    ├── 5.1 ReAct（推理 + 行动循环）
    ├── 5.2 Plan-and-Solve（规划 + 执行）
    ├── 5.3 LangChain（工程化工具集成）
    └── 5.4 AutoGPT（自主性 + 反思 + 任务循环）
```

**顺序特意安排成：** 从最底层思想 → 到工程抽象 → 再到自主框架。

你只要按顺序学，就能从序列化思维跨越到完整 Agent 系统思维。

---

## 5.1 ReAct —— Agent 思想的根基（推理 + 行动循环）

ReAct 思想是 Agent 的文学与数学基础，它不是框架，而是范式（Paradigm）。

### 核心：

```
Thought → Action → Observation → Thought → …
```

### 学习重点：

- 为什么需要 Thought/Action 分离？
- 为什么工具必须作为 Action？
- 观察（Observation）如何改变下一轮思考？
- ReAct 如何成为所有框架的根底？

### 你需要的输出能力：

- 看懂任何框架中的"ReAct 模式逻辑"
- 能手写一个最小 Agent 循环
- 理解 LLM 不是 Agent，而 Agent 是一种循环架构

**ReAct 学好了，你会得到第一层能力：**

把大模型从"回答机"变成"行动体"。

---

## 5.2 Plan-and-Solve —— 规划 + 执行模式（提高任务稳定性）

Plan-and-Solve（或 Plan-and-Execute）弥补了 ReAct 的核心弱点：

- ReAct 擅长应对动态任务
- 但对于长任务、结构化任务稳定性不够

### Plan-and-Solve 思想：

```
Plan（全局任务分解） → Solve（按计划执行） → 评估 → 修正
```

### 学习重点：

- 计划如何生成？
- 如何处理"意外情况"导致计划需要调整？
- 计划与 ReAct 结合后怎么变成混合 Agent？

### 你需要的输出能力：

- 能构建一个"生成计划 → 执行任务"的 Agent
- 能分析任务需要计划式决策还是 ReAct 决策
- 理解自主 Agent 中 planner 的重要性

**这会给你第二层能力：**

让 Agent 能执行长、多步骤、高稳定性的任务。

---

## 5.3 LangChain —— 工程化工具集成（Tool + Memory + Agent 内核）

LangChain 不是思想，而是工程化实现的集合：

### 核心组成：

- **Tool**（工具抽象层）
- **Chains**（多步骤逻辑）
- **Memory**（长期/短期记忆）
- **AgentExecutor**（运行内核）
- **ReAct / Plan-and-Execute Agent 类型**

### 学习重点：

- 工具是如何注册并暴露给 LLM 的？
- 工具调用识别的底层机制（Function calling / 格式约束）
- Memory 如何影响下一轮 Thought？
- 为什么需要 AgentExecutor（运行时管理）？
- 工程级框架如何比纯 ReAct 更稳定？

### 你需要的输出能力：

- 能理解自己的系统应该如何组织工具
- 能构建一个"工具 + 记忆 + Agent 核心循环"的框架
- 能从 LangChain 中抽取独立可复用的组件思想

**这会给你第三层能力：**

能为 Agent 构建一个真正的工程内核（runtime）。

---

## 5.4 AutoGPT —— 自主性、任务循环、反思（高级智能行为）

AutoGPT 不是为了工程，而是为了展示"自主 Agent 的未来"。

它提供你必须理解的三个重要思想：

### 1. 任务循环（Task Loop）

```
Goal → Generate Tasks → Execute → Evaluate → Generate New Tasks
```

### 2. 自我反思（Self-Reflection）

LLM 自评 → 自我修正 → 提升执行质量。

### 3. 自主性（Autonomy）

Agent 能根据观察结果自行决定下一步，而不是等待用户指令。

### 学习重点：

- 为什么 AutoGPT 容易"跑偏"？（自主性与不稳定性的矛盾）
- 自反思如何提升智能？（GPT-4 系列中的关键能力）
- 为什么现代 Agent 都要引入"限制器"？

### 你需要的输出能力：

- 能在自己的框架中加入任务管理循环
- 能设计自反思机制（Reflection）
- 能理解为何自主 Agent 需要加强约束（Safety）

**这会给你第四层能力：**

让 Agent 拥有真正的"智能行为"，而不仅是流水线执行。

---

## 总结：第五阶段四大框架的系统定位图

```
ReAct（基础思想层）
    ↓
Plan-and-Solve（任务规划层）
    ↓
LangChain（工程抽象层）
    ↓
AutoGPT（自主智能层）
```

四个模块串起来，你就能理解：

- Agent 是如何"思考"的（ReAct）
- Agent 是如何"规划任务"的（Plan）
- Agent 是如何"实践工具"的（LangChain）
- Agent 是如何"自我改进"的（AutoGPT）

**这四层组合起来，就是任何高级 Agent 系统的完整思想。**

