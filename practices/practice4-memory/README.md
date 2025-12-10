# 实践4：带记忆的 Agent

## 目标

学习如何为 Agent 添加记忆能力，让 Agent 能够记住历史对话和任务上下文。

## 核心概念

### 记忆的类型

#### 1. 短期记忆（Short-Term Memory, STM）
- **作用**：存储当前对话的上下文
- **特点**：临时性，任务结束后通常清空
- **用途**：让 Agent 理解当前对话的上下文

#### 2. 长期记忆（Long-Term Memory, LTM）
- **作用**：存储可长期复用的信息
- **特点**：持久性，跨任务保存
- **用途**：用户偏好、历史项目资料、Agent 知识

#### 3. 检索增强记忆（RAG Memory）
- **作用**：从外部知识库检索相关信息
- **特点**：动态检索，不存储所有信息
- **用途**：大规模知识库、文档检索

### 记忆如何影响 Agent？

1. **上下文理解**：记忆让 Agent 理解对话历史
2. **个性化**：长期记忆让 Agent 记住用户偏好
3. **知识增强**：RAG 记忆让 Agent 访问外部知识
4. **任务连续性**：记忆让 Agent 执行长期任务

## 设计思路

### 1. 短期记忆实现

```python
class ShortTermMemory:
    """短期记忆：存储当前对话上下文"""
    def __init__(self, max_turns: int = 10):
        self.conversations = []
        self.max_turns = max_turns
    
    def add(self, role: str, content: str):
        """添加对话"""
        self.conversations.append({"role": role, "content": content})
        # 限制长度，避免超出 token 限制
        if len(self.conversations) > self.max_turns * 2:
            self.conversations = self.conversations[-self.max_turns * 2:]
    
    def get_context(self) -> List[Dict]:
        """获取上下文"""
        return self.conversations
```

### 2. 长期记忆实现

```python
class LongTermMemory:
    """长期记忆：持久化存储"""
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.memory = self._load()
    
    def save(self, key: str, value: Any):
        """保存记忆"""
        self.memory[key] = value
        self._persist()
    
    def retrieve(self, key: str) -> Any:
        """检索记忆"""
        return self.memory.get(key)
    
    def search(self, query: str) -> List[Any]:
        """搜索记忆"""
        # 简单的关键词搜索
        results = []
        for key, value in self.memory.items():
            if query.lower() in str(value).lower():
                results.append(value)
        return results
```

### 3. 记忆集成到 Agent

```python
class AgentWithMemory:
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
    
    def run(self, query: str):
        # 1. 检索相关长期记忆
        relevant_memory = self.ltm.search(query)
        
        # 2. 获取短期记忆（对话历史）
        context = self.stm.get_context()
        
        # 3. 构建包含记忆的 Prompt
        prompt = self._build_prompt(query, context, relevant_memory)
        
        # 4. 调用 LLM
        response = self._call_llm(prompt)
        
        # 5. 更新记忆
        self.stm.add("user", query)
        self.stm.add("assistant", response)
```

## 实现要点

1. **记忆存储**：如何存储短期和长期记忆？
2. **记忆检索**：如何从记忆中检索相关信息？
3. **记忆更新**：何时更新记忆？如何避免记忆冲突？
4. **记忆压缩**：如何避免记忆过长导致 token 超限？
5. **记忆优先级**：如何决定哪些记忆更重要？

## 运行示例

```bash
python example.py
```

示例场景：
- 多轮对话：Agent 记住之前的对话内容
- 用户偏好：Agent 记住用户的偏好设置
- 任务上下文：Agent 记住正在执行的任务状态

## 学习重点

通过这个实践，你将理解：

1. ✅ **记忆的作用**：为什么 Agent 需要记忆？
2. ✅ **短期记忆**：如何实现对话上下文管理？
3. ✅ **长期记忆**：如何实现持久化记忆？
4. ✅ **记忆检索**：如何从记忆中检索相关信息？
5. ✅ **记忆管理**：如何避免记忆过长和冲突？

## 记忆管理的挑战

1. **Token 限制**：LLM 有 token 限制，不能无限存储记忆
2. **记忆选择**：如何选择最相关的记忆？
3. **记忆更新**：如何处理记忆冲突和更新？
4. **记忆压缩**：如何压缩记忆以节省 token？

## 下一步

完成这个实践后，进入 **实践5：反思机制 Agent**，学习如何让 Agent 自我评估和优化。

