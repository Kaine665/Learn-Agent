"""
实践6：多 Agent 协作系统

核心思想：理解多 Agent 系统（MAS）架构和协作机制
"""

from typing import Dict, List, Any, Optional
from openai import OpenAI
from abc import ABC, abstractmethod


class Message:
    """Agent 之间的消息"""
    
    def __init__(self, sender: str, receiver: str, content: str, msg_type: str = "request"):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = msg_type  # request, response, notification
    
    def __str__(self):
        return f"[{self.sender} -> {self.receiver}] ({self.type}): {self.content}"


class BaseAgent(ABC):
    """
    Agent 基类
    
    设计要点：
    1. 定义 Agent 的基本接口
    2. 每个 Agent 有名称、角色和专长
    3. 支持消息接收和处理
    """
    
    def __init__(self, name: str, role: str, expertise: str, api_key: str, model: str = "gpt-4.1"):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.message_history: List[Message] = []
    
    @abstractmethod
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        处理任务
        
        Args:
            task: 任务描述
            context: 上下文信息（其他 Agent 的输出）
        
        Returns:
            处理结果
        """
        pass
    
    def receive_message(self, message: Message):
        """接收消息"""
        self.message_history.append(message)
    
    def send_message(self, receiver: str, content: str, msg_type: str = "request") -> Message:
        """发送消息"""
        return Message(sender=self.name, receiver=receiver, content=content, msg_type=msg_type)
    
    def _build_prompt(self, task: str, context: Dict[str, Any] = None) -> str:
        """构建 Agent 的 Prompt"""
        prompt = f"""你是 {self.name}，角色是 {self.role}，专长是 {self.expertise}。

你的任务是：{task}
"""
        
        if context:
            prompt += "\n上下文信息：\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += "\n请基于你的专长完成任务。"
        return prompt


class ResearchAgent(BaseAgent):
    """研究 Agent：负责搜索和收集信息"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        super().__init__(
            name="ResearchAgent",
            role="研究专家",
            expertise="信息搜索、资料收集、数据整理",
            api_key=api_key,
            model=model
        )
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理研究任务"""
        prompt = self._build_prompt(task, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个研究专家，擅长搜索和整理信息。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content


class AnalysisAgent(BaseAgent):
    """分析 Agent：负责分析和评估信息"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        super().__init__(
            name="AnalysisAgent",
            role="分析专家",
            expertise="数据分析、信息评估、逻辑推理",
            api_key=api_key,
            model=model
        )
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理分析任务"""
        prompt = self._build_prompt(task, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个分析专家，擅长分析和评估信息。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content


class WriterAgent(BaseAgent):
    """写作 Agent：负责撰写内容"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        super().__init__(
            name="WriterAgent",
            role="写作专家",
            expertise="内容撰写、文章结构、文字表达",
            api_key=api_key,
            model=model
        )
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理写作任务"""
        prompt = self._build_prompt(task, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个写作专家，擅长撰写高质量内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content


class ReviewerAgent(BaseAgent):
    """审查 Agent：负责审查和优化内容"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        super().__init__(
            name="ReviewerAgent",
            role="审查专家",
            expertise="内容审查、质量评估、优化建议",
            api_key=api_key,
            model=model
        )
    
    def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """处理审查任务"""
        prompt = self._build_prompt(task, context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个审查专家，擅长评估和优化内容质量。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content


class CoordinatorAgent:
    """
    协调者 Agent
    
    设计要点：
    1. 管理多个 Agent
    2. 分解任务并分配
    3. 协调 Agent 之间的协作
    4. 整合最终结果
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_log: List[Dict] = []
    
    def register_agent(self, agent: BaseAgent):
        """注册 Agent"""
        self.agents[agent.name] = agent
        print(f"✅ 已注册 Agent: {agent.name} ({agent.role})")
    
    def _decompose_task(self, task: str) -> List[Dict[str, str]]:
        """
        分解任务
        
        设计要点：
        1. 使用 LLM 分析任务
        2. 将任务分解为子任务
        3. 为每个子任务分配 Agent
        """
        prompt = f"""你是一个任务协调专家。请将以下任务分解为子任务，并为每个子任务指定合适的 Agent。

任务：{task}

可用 Agent：
{', '.join([f"{name} ({agent.role})" for name, agent in self.agents.items()])}

请按照以下格式输出：
1. [子任务描述] -> [Agent名称]
2. [子任务描述] -> [Agent名称]
...
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个任务协调专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        decomposition = response.choices[0].message.content
        
        # 简单解析（实际应该更复杂）
        subtasks = []
        lines = decomposition.split('\n')
        for line in lines:
            if '->' in line:
                parts = line.split('->')
                if len(parts) == 2:
                    subtask = parts[0].strip()
                    agent_name = parts[1].strip()
                    subtasks.append({
                        "task": subtask,
                        "agent": agent_name
                    })
        
        return subtasks if subtasks else [{"task": task, "agent": list(self.agents.keys())[0]}]
    
    def coordinate(self, task: str) -> str:
        """
        协调任务执行
        
        设计要点：
        1. 分解任务
        2. 按顺序执行子任务
        3. 将前一个 Agent 的输出作为下一个 Agent 的输入
        4. 整合最终结果
        """
        print(f"\n{'='*50}")
        print(f"协调任务：{task}")
        print(f"{'='*50}\n")
        
        # 1. 分解任务
        print("📋 任务分解：")
        subtasks = self._decompose_task(task)
        for i, subtask in enumerate(subtasks, 1):
            print(f"  {i}. {subtask['task']} -> {subtask['agent']}")
        print()
        
        # 2. 执行子任务
        context = {}
        results = {}
        
        for i, subtask in enumerate(subtasks, 1):
            agent_name = subtask['agent']
            subtask_desc = subtask['task']
            
            if agent_name not in self.agents:
                print(f"⚠️ 警告：Agent {agent_name} 不存在，跳过")
                continue
            
            agent = self.agents[agent_name]
            
            print(f"[步骤 {i}] {agent.role} 执行：{subtask_desc}")
            
            # 执行任务
            result = agent.process(subtask_desc, context)
            results[agent_name] = result
            
            # 更新上下文
            context[agent_name] = result
            
            print(f"结果：{result[:100]}...\n")
            
            # 记录执行日志
            self.execution_log.append({
                "step": i,
                "agent": agent_name,
                "task": subtask_desc,
                "result": result
            })
        
        # 3. 整合结果
        print("📝 整合结果：")
        final_result = self._integrate_results(task, results)
        print(f"最终结果：{final_result[:200]}...\n")
        
        return final_result
    
    def _integrate_results(self, original_task: str, results: Dict[str, str]) -> str:
        """
        整合多个 Agent 的结果
        
        设计要点：
        1. 收集所有 Agent 的输出
        2. 使用 LLM 整合结果
        3. 生成最终输出
        """
        results_summary = "\n".join([
            f"{agent_name} 的输出：\n{result}\n"
            for agent_name, result in results.items()
        ])
        
        prompt = f"""原始任务：{original_task}

各 Agent 的执行结果：
{results_summary}

请整合以上结果，生成最终输出。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个结果整合专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def run(self, task: str) -> str:
        """运行协调者（协调任务执行）"""
        return self.coordinate(task)


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    # 创建协调者
    coordinator = CoordinatorAgent(api_key=api_key)
    
    # 注册 Agent
    coordinator.register_agent(ResearchAgent(api_key=api_key))
    coordinator.register_agent(AnalysisAgent(api_key=api_key))
    coordinator.register_agent(WriterAgent(api_key=api_key))
    coordinator.register_agent(ReviewerAgent(api_key=api_key))
    
    # 执行任务
    coordinator.run("写一篇关于人工智能发展历史的文章")

