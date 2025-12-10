"""
实践4：带记忆的 Agent

核心思想：理解短期记忆和长期记忆的管理机制
"""

import json
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


class ShortTermMemory:
    """
    短期记忆（STM）
    
    设计要点：
    1. 存储当前对话的上下文
    2. 限制长度，避免超出 token 限制
    3. 任务结束后可以清空
    """
    
    def __init__(self, max_turns: int = 10):
        """
        Args:
            max_turns: 最大对话轮数
        """
        self.conversations: List[Dict[str, str]] = []
        self.max_turns = max_turns
    
    def add(self, role: str, content: str):
        """
        添加对话到记忆
        
        设计要点：限制长度，保留最近的对话
        """
        self.conversations.append({"role": role, "content": content})
        
        # 限制长度：保留最近的 max_turns 轮对话
        if len(self.conversations) > self.max_turns * 2:
            self.conversations = self.conversations[-self.max_turns * 2:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取对话上下文"""
        return self.conversations.copy()
    
    def clear(self):
        """清空短期记忆"""
        self.conversations = []
    
    def __len__(self) -> int:
        return len(self.conversations)


class LongTermMemory:
    """
    长期记忆（LTM）
    
    设计要点：
    1. 持久化存储用户偏好、历史信息
    2. 支持检索和搜索
    3. 跨任务保存
    """
    
    def __init__(self, storage_path: str = "memory.json"):
        """
        Args:
            storage_path: 记忆存储文件路径
        """
        self.storage_path = storage_path
        self.memory: Dict[str, Any] = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """从文件加载记忆"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _persist(self):
        """持久化记忆到文件"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def save(self, key: str, value: Any):
        """
        保存记忆
        
        设计要点：持久化存储，支持更新
        """
        self.memory[key] = value
        self._persist()
        print(f"💾 已保存记忆：{key}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """检索记忆"""
        return self.memory.get(key)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        设计要点：简单的关键词匹配，实际应用中可以使用向量检索
        """
        results = []
        query_lower = query.lower()
        
        for key, value in self.memory.items():
            # 检查 key 或 value 中是否包含查询词
            if query_lower in key.lower() or query_lower in str(value).lower():
                results.append({
                    "key": key,
                    "value": value
                })
        
        return results
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有记忆"""
        return self.memory.copy()


class AgentWithMemory:
    """
    带记忆的 Agent
    
    设计要点：
    1. 集成短期记忆和长期记忆
    2. 在 Prompt 中包含相关记忆
    3. 自动更新记忆
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.stm = ShortTermMemory(max_turns=10)
        self.ltm = LongTermMemory()
        self.max_iterations = 10
    
    def _build_system_prompt(self, relevant_memory: List[Dict] = None) -> str:
        """
        构建系统 Prompt，包含记忆信息
        
        设计要点：
        1. 如果有相关长期记忆，加入 Prompt
        2. 告诉 Agent 如何使用记忆
        """
        base_prompt = """你是一个智能助手，能够记住对话历史和用户偏好。

你的工作方式：
1. 理解用户的查询
2. 参考之前的对话历史（短期记忆）
3. 参考用户的偏好和历史信息（长期记忆）
4. 给出合适的回答

请自然地使用记忆信息，让对话更连贯和个性化。
"""
        
        if relevant_memory:
            memory_info = "\n相关记忆信息：\n"
            for mem in relevant_memory:
                memory_info += f"- {mem['key']}: {mem['value']}\n"
            base_prompt += memory_info
        
        return base_prompt
    
    def _think(self, user_query: str, relevant_memory: List[Dict] = None) -> str:
        """
        Agent 思考并生成回答
        
        设计要点：
        1. 包含短期记忆（对话历史）
        2. 包含相关长期记忆
        3. 调用 LLM 生成回答
        """
        messages = [
            {"role": "system", "content": self._build_system_prompt(relevant_memory)}
        ]
        
        # 添加短期记忆（对话历史）
        context = self.stm.get_context()
        messages.extend(context)
        
        # 添加当前查询
        messages.append({"role": "user", "content": user_query})
        
        # 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # 更新短期记忆
        self.stm.add("user", user_query)
        self.stm.add("assistant", answer)
        
        return answer
    
    def _extract_memory_info(self, user_query: str, answer: str) -> Optional[Dict[str, Any]]:
        """
        从对话中提取需要保存到长期记忆的信息
        
        设计要点：
        1. 识别用户偏好、重要信息
        2. 使用 LLM 提取关键信息
        3. 保存到长期记忆
        """
        # 简单的启发式规则：如果用户明确说要记住，则保存
        if "记住" in user_query or "保存" in user_query or "偏好" in user_query:
            # 使用 LLM 提取关键信息
            extract_prompt = f"""从以下对话中提取需要长期记住的信息（如用户偏好、重要设置等）。

用户：{user_query}
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
                temperature=0.3
            )
            
            extracted = response.choices[0].message.content
            
            if extracted and "None" not in extracted:
                # 简单解析 key: value
                lines = extracted.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            return {"key": key, "value": value}
        
        return None
    
    def run(self, user_query: str) -> str:
        """
        运行 Agent
        
        设计要点：
        1. 检索相关长期记忆
        2. 思考并生成回答
        3. 提取并保存新记忆
        """
        print(f"\n{'='*50}")
        print(f"用户查询：{user_query}")
        print(f"{'='*50}\n")
        
        # 1. 检索相关长期记忆
        relevant_memory = self.ltm.search(user_query)
        if relevant_memory:
            print("📚 检索到相关记忆：")
            for mem in relevant_memory:
                print(f"  - {mem['key']}: {mem['value']}")
            print()
        
        # 2. 思考并生成回答
        answer = self._think(user_query, relevant_memory)
        
        print(f"回答：{answer}\n")
        
        # 3. 提取并保存新记忆
        memory_info = self._extract_memory_info(user_query, answer)
        if memory_info:
            self.ltm.save(memory_info["key"], memory_info["value"])
        
        return answer
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            "short_term_turns": len(self.stm),
            "long_term_items": len(self.ltm.get_all())
        }


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    agent = AgentWithMemory(api_key=api_key)
    
    # 示例：多轮对话
    agent.run("我喜欢喝咖啡")
    agent.run("记住我的偏好：我喜欢在早上喝咖啡")
    agent.run("我早上应该喝什么？")  # Agent 应该记住之前的偏好

