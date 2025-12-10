"""
实践1：最简 ReAct Agent

核心思想：理解 Thought-Action-Observation 循环
"""

import re
from typing import Optional, Dict, Any
from openai import OpenAI


class SimpleReActAgent:
    """
    最简化的 ReAct Agent
    
    设计要点：
    1. 使用 LLM 进行推理（Thought）
    2. 解析 LLM 输出，提取 Action
    3. 执行 Action 并观察结果（Observation）
    4. 循环直到任务完成
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        """
        初始化 Agent
        
        Args:
            api_key: OpenAI API Key
            model: 使用的模型名称
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_iterations = 10  # 最大循环次数，防止死循环
        self.conversation_history = []  # 对话历史
        
    def _build_system_prompt(self) -> str:
        """
        构建系统 Prompt
        
        这是 Agent 的"人格和工作方式基准"
        """
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
    
    def _parse_llm_output(self, output: str) -> Dict[str, Any]:
        """
        解析 LLM 输出，提取 Thought、Action 和 Action Input
        
        设计要点：使用正则表达式解析结构化输出
        """
        thought_match = re.search(r'Thought:\s*(.+?)(?=\n|$)', output, re.DOTALL)
        action_match = re.search(r'Action:\s*(\w+)', output)
        action_input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', output, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else "finish"
        action_input = action_input_match.group(1).strip() if action_input_match else None
        
        # 清理 action_input
        if action_input and action_input.lower() == "none":
            action_input = None
        
        return {
            "thought": thought,
            "action": action.lower(),
            "action_input": action_input
        }
    
    def _think(self, user_query: str, observation: Optional[str] = None) -> Dict[str, Any]:
        """
        Thought 阶段：让 LLM 思考下一步要做什么
        
        设计要点：
        1. 将对话历史、用户查询和观察结果都传给 LLM
        2. LLM 基于这些信息进行推理
        """
        # 构建消息历史
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # 添加对话历史
        for entry in self.conversation_history:
            messages.append(entry)
        
        # 添加当前查询和观察
        if observation:
            messages.append({
                "role": "user",
                "content": f"用户查询：{user_query}\n\n观察结果：{observation}\n\n请继续思考下一步行动。"
            })
        else:
            messages.append({
                "role": "user",
                "content": f"用户查询：{user_query}\n\n请开始思考和行动。"
            })
        
        # 调用 LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        output = response.choices[0].message.content
        parsed = self._parse_llm_output(output)
        
        # 记录到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": output
        })
        
        return parsed
    
    def _execute_action(self, action: str, action_input: Optional[str]) -> str:
        """
        Action 阶段：执行行动并返回观察结果
        
        设计要点：
        1. 这里是最简版本，只处理简单的计算和回答
        2. 实践2 会扩展为真正的工具调用系统
        """
        if action == "finish":
            return "任务完成"
        
        elif action == "calculate":
            # 简单的计算工具
            try:
                # 安全评估：只允许基本数学运算
                result = eval(action_input, {"__builtins__": {}}, {})
                return f"计算结果：{result}"
            except Exception as e:
                return f"计算错误：{str(e)}"
        
        elif action == "answer":
            # 直接回答
            return f"回答：{action_input}"
        
        else:
            return f"未知行动：{action}"
    
    def run(self, user_query: str) -> str:
        """
        运行 Agent 的主循环
        
        设计要点：
        1. 这是 ReAct 循环的核心实现
        2. Thought → Action → Observation → Thought → ...
        """
        self.conversation_history = []  # 重置历史
        observation = None
        
        print(f"\n{'='*50}")
        print(f"用户查询：{user_query}")
        print(f"{'='*50}\n")
        
        for iteration in range(self.max_iterations):
            print(f"[迭代 {iteration + 1}]")
            
            # 1. Thought: Agent 思考
            result = self._think(user_query, observation)
            thought = result["thought"]
            action = result["action"]
            action_input = result["action_input"]
            
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            if action_input:
                print(f"Action Input: {action_input}")
            print()
            
            # 2. Action: 执行行动
            observation = self._execute_action(action, action_input)
            print(f"Observation: {observation}\n")
            
            # 记录观察结果到历史
            self.conversation_history.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })
            
            # 3. 判断是否完成
            if action == "finish":
                print("✅ 任务完成！")
                break
            
            if iteration == self.max_iterations - 1:
                print("⚠️ 达到最大迭代次数，强制结束")
        
        return observation


if __name__ == "__main__":
    # 示例：需要设置你的 API Key
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    agent = SimpleReActAgent(api_key=api_key)
    
    # 测试示例
    agent.run("计算 123 + 456")

