# 第四章：Agent 实现框架

## 本章重点

本章将介绍当前主流 Agent 框架与方法论，包括：

- LangChain
- ReAct
- AutoGPT
- OpenAI Agents
- Meta Agentic Workflow
- 工具链架构

这一章是从"理论"走向"工程实践"的关键，让你知道现实世界中 Agent 系统是如何构建的。

---

## 4.1 三类 Agent 实现思路（顶层总结）

现在构建 Agent 有三种主流路线：

### 路线 A：基于 Prompt + ReAct 模式自己写

**特点：**

- 简单
- 通用
- 灵活
- 可以零成本实现小 Agent

**适合：** 个人、小项目。

### 路线 B：使用成熟 Agent 框架（LangChain、AutoGPT、Microsoft Autogen 等）

**特点：**

- 工具集成丰富
- 框架定义完善
- 多 Agent 协作方便

**适合：** 企业、复杂系统。

### 路线 C：使用模型厂商的原生 Agent API（OpenAI Agents、Gemini Tool Use 等）

**特点：**

- 最稳
- 最强
- 最未来趋势

**适合：** 生产级应用。

下面我们逐一展开。

---

## 4.2 ReAct 框架（最基础、最经典的 Agent 方法）

**ReAct = Reasoning + Acting**

是现代 Agent 的基础思想，几乎所有框架都是 ReAct 的变体。

### 流程：

```
Thought → Action → Observation → Thought → Action → …
```

### 典型工具调用格式：

```
Thought: 我需要搜索信息
Action: search("LLM history")
Observation: 返回搜索结果
Thought: 我将从结果中筛选...
```

### ReAct 优点

- 灵活
- 自主决策
- 对未知情况鲁棒

### ReAct 缺点

- 对于长任务不稳定
- 缺少高层规划
- 工具调用可能混乱

因此出现了 Plan-and-Execute 和反思机制补强。

---

## 4.3 LangChain（最完整、工业界使用最广的 Agent 框架）

LangChain 提供：

- 工具集成工具（Tool）
- Memory 管理
- AgentExecutor
- 规划器（Plan-and-Execute Agent）
- 文档加载与检索（Loader + VectorStore）

### LangChain 中 Agent 的组成：

```
LLM + Tools + AgentType + Memory + AgentExecutor
```

### 典型结构：

```python
agent = initialize_agent(
    tools=[search, calculator, web_browser],
    llm=OpenAI(),
    agent=AgentType.REACT,
    memory=ConversationBufferMemory(),
)
```

**使用方式本质是：**

让 LLM 自主决定什么时候调用工具。

### LangChain Agent 优势

- 工具集成强大
- 有多种 Agent 模型（ReAct、Plan+Execute、Self-Ask等）
- 社区生态庞大
- 适合企业级应用

### LangChain Agent 缺点

- 复杂度高
- Prompt 大量依赖系统配置
- 执行链长、延迟高

---

## 4.4 AutoGPT（自主演化 Agent 框架）

AutoGPT 是最早的"自主 AI"实验框架之一。

### AutoGPT 特点

- 拥有持续目标循环
- 自动规划（Goal → Task List）
- 自动工具调用
- 自我反思
- 能生成新任务

### AutoGPT Loop：

```
目标 → 计划 → 执行 → 反思 → 更新计划 → 执行 → ...
```

### 缺点

- 不稳定
- 幻觉严重
- 太自由、自我循环容易乱跑
- 工具调用不可控

现代版本已经改进，但整体仍更像实验用途，而非生产用途。

---

## 4.5 Microsoft AutoGen（多 Agent 协作框架）

AutoGen 的核心理念：

**多个 Agent 互相对话 → 协作完成任务**

### 示例：

- **UserProxy Agent**（任务管理）
- **Assistant Agent**（知识推理）
- **Coder Agent**（写代码）
- **Executor Agent**（运行代码）

它像是一个虚拟团队。

### 优点：

- 适合复杂任务
- 分工明确
- 可插拔工具
- 能优化工程流程（例如软件开发）

### 缺点：

- 资源消耗大
- 复杂度高

---

## 4.6 OpenAI Agents（未来标准）

这是最新、工业界最看好的方向。

OpenAI 的 Agent API（包括 Assistants v2 → Agents）具备：

### 1）原生 Tool Use

平台级支持：

- Web search
- Code Interpreter
- Retrieval
- Custom Tools
- File management
- Function calling（API）

### 2）自动规划

Agent 自动拆解任务，无需人为写复杂 prompt。

### 3）自动记忆管理

系统自动决定：

- 何时存储信息
- 何时检索
- 何时重写记忆

### 4）可部署、可扩展

适合集成进工作流、应用和企业生产。

### 优势总结：

- 最稳
- 最强
- 最容易使用
- 工具调用最智能
- 最少幻觉

这是未来 Agent 的工业标准。

---

## 4.7 对比：四大 Agent 框架优缺点

| 框架 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| ReAct（手写） | 灵活、简单 | 需手工维护逻辑 | 小项目、教学 |
| LangChain | 工具丰富、生态强 | 配置复杂 | 企业级应用 |
| AutoGPT | 强自主性 | 不稳定 | 研究、实验 |
| AutoGen（多 Agent） | 多 Agent 协作强 | 架构复杂 | 复杂专业任务 |
| OpenAI Agents | 最强大、最稳定 | 绑定生态 | 生产应用、app开发 |

---

## 4.8 多 Agent 系统（MAS）架构

MAS 的核心思想：

将任务分配给不同 Agent，每个 Agent 是专家。

### 例如：

- **Research Agent** → 搜资料  
- **Analysis Agent** → 判断有效性  
- **Writer Agent** → 写最终文稿  
- **Reviewer Agent** → 优化结构  

### 多 Agent 优势：

- 专业化
- 并行性
- 可审校
- 高质量输出

### 缺点：

- 成本高
- 协作复杂

