# LLM 职责分离设计原则

## 核心洞察

> **LLM 不是"万能 prompt 机器"，不能通过一个万能 prompt 一次性把事情做好。**

### 人脑 vs LLM 的根本区别

**人脑的特点：**
- ✅ 可以同时处理多个任务（并行处理）
- ✅ 一个指令可以同时完成多个目标
- ✅ 上下文理解能力强，能自动关联
- ✅ 能够"一心多用"

**LLM 的特点：**
- ❌ 每次调用只能专注一个任务
- ❌ 一个 prompt 很难同时做好多件事
- ❌ 需要明确的指令和结构化的输出
- ❌ 多任务时容易"顾此失彼"

---

## 问题：为什么不能"一个 prompt 做所有事"？

### 当前实现的问题

在 `practice4-memory/agent.py` 中，当前实现存在职责混乱：

```python
# 第一次调用：生成回答
def _think(self, user_query: str, relevant_memory: List[Dict] = None) -> str:
    """Agent 思考并生成回答"""
    response = self.client.chat.completions.create(...)
    answer = response.choices[0].message.content
    return answer

# 第二次调用：提取记忆
def _extract_memory_info(self, user_query: str, answer: str) -> Optional[Dict]:
    """从对话中提取需要保存到长期记忆的信息"""
    # 又调用一次 LLM
    response = self.client.chat.completions.create(...)
    extracted = response.choices[0].message.content
    return extracted
```

**问题：**
1. 每次对话需要调用两次 LLM
2. 职责混乱：一个 Agent 既要回答用户问题，又要管理记忆
3. 效率低：两次调用增加了延迟和成本

### 为什么不能合并成一个 prompt？

如果尝试在一个 prompt 里同时做两件事：

```python
# ❌ 不好的方式：一个 prompt 做两件事
prompt = """回答用户问题，同时提取需要记住的信息。

用户：{user_query}

请：
1. 给出回答
2. 提取记忆（格式：key: value）

输出格式：
回答：xxx
记忆：key: value 或 None
"""
```

**问题：**
- ❌ LLM 可能只做好一件事（回答或提取）
- ❌ 输出格式不稳定，解析困难
- ❌ 难以控制两个任务的优先级
- ❌ 如果回答很长，记忆提取可能被忽略
- ❌ 无法针对不同任务使用不同的 temperature 和 prompt 风格

---

## 解决方案：职责分离

### 核心原则

> **一个 LLM 调用，一个明确目标**

### 为什么需要分离？

#### 1. 任务性质不同

- **回答用户问题**：需要创造性、灵活性、高 temperature
- **提取记忆**：需要精确性、结构化、低 temperature

#### 2. LLM 的局限性

- 不能同时保证"回答得好"和"提取得准"
- 需要不同的 temperature、不同的 prompt 风格
- 多任务时容易"顾此失彼"

#### 3. 可维护性

- 分离后可以独立优化
- 可以替换不同的提取策略（规则、LLM、混合）
- 易于调试和测试

---

## 更好的设计方案

### 方案 1：独立的记忆管理模块（推荐）

```python
class MemoryExtractor:
    """独立的记忆提取模块"""
    
    def extract(self, user_query: str, answer: str) -> Optional[Dict]:
        """
        提取记忆
        
        设计要点：
        1. 使用规则优先（快速、准确）
        2. 复杂情况才用 LLM（慢但灵活）
        3. 输出格式固定（便于解析）
        """
        # 规则1：明确指令（最快）
        if "记住" in user_query:
            return self._extract_by_rule(user_query)
        
        # 规则2：模式匹配（次快）
        if self._has_memory_pattern(user_query):
            return self._extract_by_pattern(user_query)
        
        # 规则3：LLM 提取（最慢，但最灵活）
        return self._extract_by_llm(user_query, answer)
    
    def _extract_by_rule(self, query: str) -> Optional[Dict]:
        """规则提取：快速、准确"""
        # "记住我的偏好：xxx" -> key: 偏好, value: xxx
        if "偏好" in query:
            value = query.replace("记住", "").replace("我的偏好：", "").strip()
            return {"key": "偏好", "value": value}
        # ... 更多规则
    
    def _extract_by_llm(self, query: str, answer: str) -> Optional[Dict]:
        """LLM 提取：复杂情况才用"""
        # 只在规则无法处理时使用
        # 使用更严格的 prompt 和更低的 temperature
        extract_prompt = f"""从以下对话中提取需要长期记住的信息。

用户：{query}
助手：{answer}

请提取关键信息，格式：key: value
如果没有需要记住的信息，输出 None。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个信息提取专家。"},
                {"role": "user", "content": extract_prompt}
            ],
            temperature=0.3  # 低 temperature，保证精确性
        )
        
        # 解析输出
        extracted = response.choices[0].message.content
        # ... 解析逻辑


class MemoryManager:
    """独立的记忆管理模块"""
    
    def __init__(self, storage_path: str = "memory.json"):
        self.ltm = LongTermMemory(storage_path)
        self.extractor = MemoryExtractor()
    
    def retrieve(self, query: str) -> List[Dict]:
        """检索相关记忆"""
        return self.ltm.search(query)
    
    def save(self, key: str, value: Any):
        """保存记忆"""
        self.ltm.save(key, value)
    
    def extract_and_save(self, user_query: str, answer: str) -> Optional[Dict]:
        """从对话中提取并保存记忆"""
        memory_info = self.extractor.extract(user_query, answer)
        if memory_info:
            self.save(memory_info["key"], memory_info["value"])
        return memory_info


class AgentWithMemory:
    """主 Agent：只负责回答用户问题"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.stm = ShortTermMemory(max_turns=10)
        self.memory_manager = MemoryManager()  # 独立的记忆管理模块
    
    def _think(self, user_query: str, relevant_memory: List[Dict] = None) -> str:
        """只负责生成回答（专注一件事）"""
        messages = [
            {"role": "system", "content": self._build_system_prompt(relevant_memory)}
        ]
        
        # 添加短期记忆（对话历史）
        context = self.stm.get_context()
        messages.extend(context)
        
        # 添加当前查询
        messages.append({"role": "user", "content": user_query})
        
        # 调用 LLM（只做一件事：生成回答）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7  # 适合创造性回答
        )
        
        answer = response.choices[0].message.content
        
        # 更新短期记忆
        self.stm.add("user", user_query)
        self.stm.add("assistant", answer)
        
        return answer
    
    def run(self, user_query: str) -> str:
        """
        运行 Agent
        
        设计要点：
        1. 检索记忆（记忆模块负责）
        2. 生成回答（主 Agent 负责）
        3. 保存记忆（记忆模块负责）
        """
        # 1. 检索记忆（记忆模块负责）
        relevant_memory = self.memory_manager.retrieve(user_query)
        
        # 2. 生成回答（主 Agent 负责，专注一件事）
        answer = self._think(user_query, relevant_memory)
        
        # 3. 保存记忆（记忆模块负责，使用规则或 LLM）
        self.memory_manager.extract_and_save(user_query, answer)
        
        return answer
```

### 方案 2：使用 Function Calling 在一次调用中完成

如果模型支持 function calling，可以在一次调用中同时返回回答和记忆：

```python
def _think(self, user_query: str, relevant_memory: List[Dict] = None) -> tuple[str, Optional[Dict]]:
    """返回回答和需要保存的记忆"""
    
    # 定义 function calling
    functions = [{
        "name": "save_memory",
        "description": "保存需要长期记住的信息",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "记忆的键"},
                "value": {"type": "string", "description": "记忆的值"}
            }
        }
    }]
    
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[...],
        functions=functions,
        function_call="auto"
    )
    
    # 解析回答和记忆
    answer = response.choices[0].message.content
    memory_info = None
    
    if response.choices[0].message.function_call:
        # 提取记忆信息
        memory_info = json.loads(response.choices[0].message.function_call.arguments)
    
    return answer, memory_info
```

**优点：**
- ✅ 一次调用完成两件事
- ✅ 输出格式固定（JSON）

**缺点：**
- ❌ 需要模型支持 function calling
- ❌ 仍然存在"一个 prompt 做两件事"的问题
- ❌ 难以针对不同任务使用不同的 temperature

### 方案 3：使用结构化输出（如果模型支持）

```python
def _think(self, user_query: str, relevant_memory: List[Dict] = None) -> tuple[str, Optional[Dict]]:
    """使用结构化输出同时返回回答和记忆"""
    
    prompt = f"""回答用户问题，同时判断是否需要保存记忆。

用户：{user_query}

请以 JSON 格式输出：
{{
    "answer": "你的回答",
    "memory": {{"key": "记忆键", "value": "记忆值"}} 或 null
}}
"""
    
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[...],
        response_format={"type": "json_object"}  # 如果模型支持
    )
    
    result = json.loads(response.choices[0].message.content)
    return result["answer"], result.get("memory")
```

---

## 核心原则总结

### 1. 一个 LLM 调用，一个明确目标

**为什么？**

- ✅ **可控性**：每个调用有明确目标，容易调试和优化
- ✅ **可靠性**：避免"做了 A 但忘了 B"的情况
- ✅ **效率**：可以针对不同任务使用不同策略（规则 vs LLM）
- ✅ **可扩展**：新任务可以独立添加，不影响现有功能

### 2. 分离职责，独立模块

**为什么？**

- ✅ **任务性质不同**：需要不同的处理方式
- ✅ **LLM 的局限性**：不能同时保证多个任务的质量
- ✅ **可维护性**：独立优化、独立测试、独立替换

### 3. 规则优先，LLM 补充

**为什么？**

- ✅ **效率**：规则提取快速、准确
- ✅ **成本**：减少 LLM 调用次数
- ✅ **可靠性**：规则更稳定，LLM 更灵活

---

## 实践建议

### 1. 识别需要分离的任务

以下情况需要分离：

- ✅ 任务性质不同（创造性 vs 精确性）
- ✅ 需要不同的 temperature
- ✅ 需要不同的 prompt 风格
- ✅ 输出格式不同

### 2. 设计独立的模块

```python
# ✅ 好的设计：职责分离
class TaskA:
    """专门处理任务 A"""
    pass

class TaskB:
    """专门处理任务 B"""
    pass

class MainAgent:
    """主 Agent，协调各个模块"""
    def __init__(self):
        self.task_a = TaskA()
        self.task_b = TaskB()
```

### 3. 规则优先，LLM 补充

```python
def extract(self, input_data):
    # 1. 先尝试规则（快速、准确）
    if self._can_extract_by_rule(input_data):
        return self._extract_by_rule(input_data)
    
    # 2. 复杂情况才用 LLM（慢但灵活）
    return self._extract_by_llm(input_data)
```

### 4. 明确每个调用的目标

```python
# ✅ 好的方式：每个调用有明确目标
answer = self._generate_answer(user_query)  # 目标：生成回答
memory = self._extract_memory(user_query)   # 目标：提取记忆

# ❌ 不好的方式：一个调用做两件事
result = self._do_everything(user_query)  # 目标不明确
```

---

## 类比：工厂流水线

就像工厂流水线：

- ❌ **不能要求一个工人同时"组装"和"质检"**
- ✅ **需要分工：组装工人专注组装，质检工人专注质检**
- ✅ **虽然多了一个步骤，但质量和效率都更高**

---

## 总结

### 核心洞察

1. **LLM 不是万能 prompt 机器**：不能一个 prompt 同时做好多件事
2. **需要分离职责**：不同任务需要不同的处理方式
3. **独立模块的必要性**：记忆管理需要专门的模块，而不是混在主任务里

### 设计原则

1. **一个 LLM 调用，一个明确目标**
2. **分离职责，独立模块**
3. **规则优先，LLM 补充**

### 实践要点

1. 识别需要分离的任务
2. 设计独立的模块
3. 规则优先，LLM 补充
4. 明确每个调用的目标

这不是"过度设计"，而是**适应 LLM 特性的必要设计**。

---

## 参考：当前实现的问题

在 `practice4-memory/agent.py` 中：

```python
# 问题1：职责混乱
class AgentWithMemory:
    def _think(self, ...):      # 生成回答
        pass
    
    def _extract_memory_info(self, ...):  # 提取记忆
        pass  # 又调用一次 LLM

# 问题2：效率低
# 每次对话需要调用两次 LLM

# 问题3：难以优化
# 两个任务混在一起，难以独立优化
```

**改进方向：**

```python
# ✅ 改进：职责分离
class MemoryManager:
    """独立的记忆管理模块"""
    pass

class AgentWithMemory:
    """主 Agent：只负责回答"""
    def __init__(self):
        self.memory_manager = MemoryManager()  # 独立的模块
    
    def _think(self, ...):
        """只负责生成回答"""
        pass
```

---

## 延伸阅读

- [Plan Agent 问题诊断与改进思路](./Plan%20Agent%20问题诊断与改进思路.md)
- [显式思考系统设计](./显式思考系统设计.md)
- [上下文优化思考](./上下文优化思考.md)

