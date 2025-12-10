"""
实践2：工具集成 Agent

核心思想：理解工具调用机制和工具注册系统
"""

import re
from typing import Optional, Dict, Any, List, Callable
from openai import OpenAI


class Tool:
    """
    工具基类
    
    设计要点：
    1. 统一的工具接口
    2. 工具描述用于告诉 LLM 工具的能力
    3. 工具函数是实际执行逻辑
    """
    
    def __init__(self, name: str, description: str, func: Callable):
        """
        Args:
            name: 工具名称（LLM 通过这个名称调用工具）
            description: 工具描述（告诉 LLM 工具能做什么）
            func: 工具函数（实际执行逻辑）
        """
        self.name = name
        self.description = description
        self.func = func
    
    def execute(self, *args, **kwargs) -> Any:
        """执行工具"""
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    
    def __str__(self) -> str:
        """工具的描述字符串，用于生成 Prompt"""
        return f"{self.name}: {self.description}"


class ToolIntegratedAgent:
    """
    带工具集成的 ReAct Agent
    
    设计要点：
    1. 工具注册系统
    2. 工具描述自动生成
    3. 工具调用机制
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_iterations = 10
        self.conversation_history = []
        self.tools: Dict[str, Tool] = {}  # 工具注册表
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 计算器工具
        def calculator(expression: str) -> str:
            """计算数学表达式"""
            try:
                # 安全评估：只允许基本数学运算
                allowed_chars = set('0123456789+-*/()., ')
                if all(c in allowed_chars for c in expression):
                    result = eval(expression, {"__builtins__": {}}, {})
                    return str(result)
                else:
                    return "错误：表达式包含不允许的字符"
            except Exception as e:
                return f"计算错误：{str(e)}"
        
        self.register_tool(
            name="calculator",
            description="计算数学表达式，例如：calculator('123 + 456')",
            func=calculator
        )
        
        # 搜索工具（模拟）
        def search(query: str) -> str:
            """搜索信息（模拟）"""
            # 这里是模拟搜索，实际应该调用真实搜索 API
            return f"搜索结果（模拟）：关于 '{query}' 的信息..."
        
        self.register_tool(
            name="search",
            description="搜索信息，例如：search('Python 教程')",
            func=search
        )
    
    def register_tool(self, name: str, description: str, func: Callable):
        """
        注册工具
        
        设计要点：这是工具系统的核心，允许动态添加工具
        """
        tool = Tool(name=name, description=description, func=func)
        self.tools[name] = tool
        print(f"✅ 已注册工具：{name}")
    
    def _build_system_prompt(self) -> str:
        """
        构建系统 Prompt，包含工具描述
        
        设计要点：
        1. 告诉 LLM 有哪些工具可用
        2. 告诉 LLM 如何使用工具
        3. 明确输出格式
        """
        # 生成工具列表
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools.values()
        ])
        
        return f"""你是一个智能助手，能够通过思考和行动来解决问题。

你可以使用以下工具：
{tools_desc}

你的工作方式遵循 ReAct 模式：
1. **Thought（思考）**：分析当前情况，思考下一步要做什么
2. **Action（行动）**：决定执行什么行动（可以是工具名称或 finish）
3. **Action Input（行动输入）**：工具所需的参数

请严格按照以下格式输出：

Thought: [你的思考过程]
Action: [工具名称，如：calculator, search, finish]
Action Input: [工具参数，如果没有则写 None]

当任务完成时，使用 Action: finish 来结束。

示例：
用户：计算 10 + 20
Thought: 用户要求计算 10 + 20，我应该使用 calculator 工具
Action: calculator
Action Input: 10 + 20
"""
    
    def _parse_llm_output(self, output: str) -> Dict[str, Any]:
        """解析 LLM 输出"""
        thought_match = re.search(r'Thought:\s*(.+?)(?=\n|$)', output, re.DOTALL)
        action_match = re.search(r'Action:\s*(\w+)', output)
        action_input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', output, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else "finish"
        action_input = action_input_match.group(1).strip() if action_input_match else None
        
        if action_input and action_input.lower() == "none":
            action_input = None
        
        return {
            "thought": thought,
            "action": action.lower(),
            "action_input": action_input
        }
    
    def _think(self, user_query: str, observation: Optional[str] = None) -> Dict[str, Any]:
        """Thought 阶段"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        for entry in self.conversation_history:
            messages.append(entry)
        
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
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        output = response.choices[0].message.content
        parsed = self._parse_llm_output(output)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": output
        })
        
        return parsed
    
    def _execute_action(self, action: str, action_input: Optional[str]) -> str:
        """
        Action 阶段：执行工具调用
        
        设计要点：
        1. 检查工具是否存在
        2. 调用工具并返回结果
        3. 错误处理
        """
        if action == "finish":
            return "任务完成"
        
        # 查找工具
        if action not in self.tools:
            return f"错误：未知工具 '{action}'。可用工具：{', '.join(self.tools.keys())}"
        
        tool = self.tools[action]
        
        # 执行工具
        try:
            # 如果 action_input 是字符串，可能需要解析
            if action_input:
                # 简单处理：如果是字符串参数，去掉引号
                if action_input.startswith('"') and action_input.endswith('"'):
                    action_input = action_input[1:-1]
                elif action_input.startswith("'") and action_input.endswith("'"):
                    action_input = action_input[1:-1]
                
                result = tool.execute(action_input)
            else:
                result = tool.execute()
            
            return str(result)
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    
    def run(self, user_query: str) -> str:
        """运行 Agent 主循环"""
        self.conversation_history = []
        observation = None
        
        print(f"\n{'='*50}")
        print(f"用户查询：{user_query}")
        print(f"{'='*50}\n")
        
        for iteration in range(self.max_iterations):
            print(f"[迭代 {iteration + 1}]")
            
            # Thought
            result = self._think(user_query, observation)
            thought = result["thought"]
            action = result["action"]
            action_input = result["action_input"]
            
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            if action_input:
                print(f"Action Input: {action_input}")
            print()
            
            # Action
            observation = self._execute_action(action, action_input)
            print(f"Observation: {observation}\n")
            
            self.conversation_history.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })
            
            # 判断完成
            if action == "finish":
                print("✅ 任务完成！")
                break
            
            if iteration == self.max_iterations - 1:
                print("⚠️ 达到最大迭代次数，强制结束")
        
        return observation


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    agent = ToolIntegratedAgent(api_key=api_key)
    agent.run("计算 123 * 456")

