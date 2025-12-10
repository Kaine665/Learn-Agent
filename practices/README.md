# Agent 实践项目

通过实际编码深入理解 Agent 框架的设计思想。

## 实践路径

### 实践 1：最简 ReAct Agent

**目标：** 理解 Thought-Action-Observation 循环的核心机制

**核心概念：**

- ReAct = Reasoning + Acting
- 循环：Thought → Action → Observation → Thought → ...

**你将学到：**

- 为什么需要分离思考和行动？
- Observation 如何影响下一轮思考？
- 最基础的 Agent 循环如何工作？

---

### 实践 1.1：Function Calling Agent（可选）

**目标：** 学习使用 Function Calling 让 LLM 直接返回结构化数据

**核心概念：**

- Function Calling vs 正则解析
- 结构化数据返回
- 现代 Agent 框架的标准方式

**你将学到：**

- 为什么 Function Calling 比正则解析更可靠？
- 如何定义函数 Schema？
- LLM 如何返回结构化数据？

**建议：** 完成实践1后，对比学习实践1.1，理解两种方式的差异。

---

### 实践 2：工具集成 Agent

**目标：** 理解工具调用机制和工具注册系统

**核心概念：**

- Tool Use 是现代 Agent 的核心能力
- 工具抽象层（Tool Abstraction）
- 工具调用识别机制

**你将学到：**

- 如何设计工具接口？
- LLM 如何选择和使用工具？
- 工具调用的完整流程是什么？

---

### 实践 3：Plan-and-Execute Agent

**目标：** 理解规划与执行模式，解决长任务稳定性问题

**核心概念：**

- Plan-and-Execute = 规划 + 执行
- 任务分解（Task Decomposition）
- 计划调整机制

**你将学到：**

- 如何生成任务计划？
- 如何处理计划执行中的意外？
- 规划模式与 ReAct 的区别？

---

### 实践 4：带记忆的 Agent

**目标：** 理解短期记忆和长期记忆的管理机制

**核心概念：**

- 短期记忆（STM）：当前对话上下文
- 长期记忆（LTM）：历史经验、用户偏好
- 记忆检索（Memory Retrieval）

**你将学到：**

- 记忆如何影响 Agent 决策？
- 如何设计记忆存储和检索？
- 短期记忆和长期记忆如何协同？

---

### 实践 5：反思机制 Agent

**目标：** 理解自我评估、错误恢复和结果优化

**核心概念：**

- 自我检视（Self-Critique）
- 错误恢复（Error Recovery）
- 结果优化（Self-Refine）

**你将学到：**

- Agent 如何自我评估？
- 如何设计反思循环？
- 反思如何提升 Agent 智能？

---

### 实践 6：多 Agent 协作系统

**目标：** 理解多 Agent 系统（MAS）架构和协作机制

**核心概念：**

- Multi-Agent System（MAS）
- Agent 分工与协作
- 任务分配与协调

**你将学到：**

- 如何设计多 Agent 系统？
- Agent 之间如何通信？
- 如何实现专业化分工？

---

## 使用说明

每个实践项目都是独立的，包含：

- `agent.py` - Agent 核心实现
- `tools.py` - 工具定义（如需要）
- `example.py` - 示例运行脚本
- `README.md` - 详细说明文档

建议按顺序学习，每个实践都建立在前一个的基础上。

## 环境要求

- Python 3.8+
- OpenAI API Key（或其他 LLM API）
- 可选：LangChain（用于对比学习）

## 开始实践

```bash
# 进入第一个实践项目
cd practice1-react-basic

# 查看说明
cat README.md

# 运行示例
python example.py
```
