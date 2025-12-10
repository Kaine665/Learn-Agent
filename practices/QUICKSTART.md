# 快速开始指南

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

在 Windows PowerShell：
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

在 Linux/Mac：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

或者创建 `.env` 文件：
```
OPENAI_API_KEY=your-api-key-here
```

## 实践路径

### 第一步：最简 ReAct Agent

理解 Agent 的基础循环机制。

```bash
cd practice1-react-basic
python example.py
```

**学习目标：**
- ✅ 理解 Thought-Action-Observation 循环
- ✅ 理解 LLM 在 Agent 中的作用
- ✅ 理解格式约束的重要性

---

### 第二步：工具集成 Agent

学习如何让 Agent 真正"行动"起来。

```bash
cd practice2-tool-integration
python example.py
```

**学习目标：**
- ✅ 理解工具抽象和注册机制
- ✅ 理解工具调用流程
- ✅ 理解如何让 LLM 选择工具

---

### 第三步：Plan-and-Execute Agent

学习如何让 Agent 执行长任务。

```bash
cd practice3-plan-execute
python example.py
```

**学习目标：**
- ✅ 理解规划与执行模式
- ✅ 理解任务分解机制
- ✅ 理解计划调整策略

---

### 第四步：带记忆的 Agent

学习如何让 Agent 记住历史信息。

```bash
cd practice4-memory
python example.py
```

**学习目标：**
- ✅ 理解短期记忆和长期记忆
- ✅ 理解记忆检索机制
- ✅ 理解记忆管理策略

---

### 第五步：反思机制 Agent

学习如何让 Agent 自我评估和优化。

```bash
cd practice5-reflection
python example.py
```

**学习目标：**
- ✅ 理解反思机制的作用
- ✅ 理解错误恢复策略
- ✅ 理解结果优化流程

---

### 第六步：多 Agent 协作系统

学习如何设计多 Agent 系统。

```bash
cd practice6-multi-agent
python example.py
```

**学习目标：**
- ✅ 理解多 Agent 架构
- ✅ 理解任务分配机制
- ✅ 理解 Agent 协作流程

---

## 学习建议

### 1. 按顺序学习

每个实践都建立在前一个的基础上，建议按顺序完成。

### 2. 动手修改

不要只是运行代码，尝试：
- 修改 Prompt
- 添加新工具
- 调整 Agent 行为
- 实验不同参数

### 3. 对比理解

完成每个实践后，思考：
- 这个实践解决了什么问题？
- 相比前一个实践，有什么改进？
- 实际框架（如 LangChain）是如何实现的？

### 4. 记录笔记

记录你的：
- 理解要点
- 遇到的问题
- 改进想法
- 设计思考

---

## 常见问题

### Q: API Key 在哪里获取？

A: 访问 [OpenAI Platform](https://platform.openai.com/) 注册账号并获取 API Key。

### Q: 可以使用其他 LLM 吗？

A: 可以！修改代码中的 `OpenAI` 客户端为其他 LLM 的客户端即可。

### Q: 如何减少 API 调用成本？

A: 
1. 使用较小的模型（如 gpt-3.5-turbo）
2. 减少最大迭代次数
3. 限制对话历史长度

### Q: 代码运行出错怎么办？

A: 
1. 检查 API Key 是否正确设置
2. 检查网络连接
3. 查看错误信息，通常是 API 调用失败或格式解析错误

---

## 下一步

完成所有实践后，你可以：

1. **深入学习框架**
   - 研究 LangChain 的实现
   - 研究 AutoGPT 的架构
   - 研究 OpenAI Agents API

2. **构建自己的 Agent**
   - 设计特定领域的 Agent
   - 集成真实工具（搜索、数据库等）
   - 优化性能和成本

3. **探索高级主题**
   - RAG（检索增强生成）
   - 向量数据库
   - Agent 编排
   - 多模态 Agent

---

## 实践总结

完成所有6个实践后，你将深入理解：

1. ✅ **ReAct 循环**：Agent 的基础工作模式
2. ✅ **工具使用**：Agent 的行动能力
3. ✅ **规划执行**：长任务的稳定性
4. ✅ **记忆管理**：上下文和历史信息
5. ✅ **反思机制**：自我评估和优化
6. ✅ **多 Agent 协作**：复杂任务的解决方案

这些知识将帮助你理解现代 Agent 框架的设计思想，并能够设计和实现自己的 Agent 系统。

祝你学习愉快！🚀

