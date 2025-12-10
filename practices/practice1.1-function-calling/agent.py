"""
实践1.1：Function Calling Agent

核心思想：使用 Function Calling 让 LLM 直接返回结构化数据
"""

import json
from typing import Optional, Dict, Any, List, Callable
from openai import OpenAI


class FunctionCallingAgent:
    """
    使用 Function Calling 的 ReAct Agent
    
    设计要点：
    1. 使用 Function Calling 替代正则解析
    2. LLM 直接返回结构化数据
    3. 更可靠、更现代的实现方式
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        初始化 Agent
        
        Args:
            api_key: OpenAI API Key
            model: 使用的模型名称（Function Calling 需要 gpt-3.5-turbo 或更高版本）
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_iterations = 10
        self.conversation_history = []
        self.tools: Dict[str, Callable] = {}  # 工具函数注册表
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 计算器工具
        def calculate(expression: str) -> str:
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
        
        self.register_tool("calculate", calculate)
        
        # 搜索工具（模拟）
        def search(query: str) -> str:
            """搜索信息（模拟）"""
            return f"搜索结果（模拟）：关于 '{query}' 的信息..."
        
        self.register_tool("search", search)
    
    def register_tool(self, name: str, func: Callable):
        """
        注册工具
        
        设计要点：工具函数会被转换为 Function Calling 定义
        """
        self.tools[name] = func
        print(f"✅ 已注册工具：{name}")
    
    def _build_functions_schema(self) -> List[Dict[str, Any]]:
        """
        构建 Function Calling 的函数定义
        
        设计要点：
        1. 将工具函数转换为 JSON Schema
        2. 告诉 LLM 有哪些函数可用
        3. 定义函数参数
        """
        functions = []
        
        # 为每个工具创建函数定义
        for name, func in self.tools.items():
            # 获取函数签名（简化版，实际应该用 inspect 模块）
            if name == "calculate":
                function_def = {
                    "name": "calculate",
                    "description": "计算数学表达式，例如：123 + 456",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "要计算的数学表达式"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            elif name == "search":
                function_def = {
                    "name": "search",
                    "description": "搜索信息，例如：搜索 Python 教程",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词"
                            }
                        },
                        "required": ["query"]
                    }
                }
            else:
                # 通用函数定义
                function_def = {
                    "name": name,
                    "description": f"执行 {name} 操作",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            
            functions.append(function_def)
        
        return functions
    
    def _build_system_prompt(self) -> str:
        """
        构建系统 Prompt
        
        设计要点：
        1. Function Calling 模式下，Prompt 可以更简单
        2. 不需要强制格式约束（因为函数调用是结构化的）
        """
        return """你是一个智能助手，能够通过思考和行动来解决问题。

你的工作方式遵循 ReAct 模式：
1. **Thought（思考）**：分析当前情况，思考下一步要做什么
2. **Action（行动）**：决定执行什么行动（通过调用函数）
3. **Observation（观察）**：观察行动的结果

当任务完成时，直接回答用户，不需要调用函数。
"""
    
    def _think(self, user_query: str, observation: Optional[str] = None) -> Dict[str, Any]:
        """
        Thought 阶段：让 LLM 思考下一步要做什么
        
        设计要点：
        1. 使用 Function Calling，LLM 可以直接返回结构化数据
        2. 无需正则解析
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
        
        # 构建函数定义
        functions = self._build_functions_schema()
        
        # 调用 LLM（使用 Function Calling）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=functions,  # ← 提供函数定义
            function_call="auto",  # ← 让 LLM 自动决定是否调用函数
            temperature=0.7
        )
        
        message = response.choices[0].message
        result = {}
        
        # 检查是否调用了函数
        if message.function_call:
            # LLM 决定调用函数
            function_name = message.function_call.name
            arguments = json.loads(message.function_call.arguments)
            
            result = {
                "thought": f"决定调用函数 {function_name}",
                "action": function_name,
                "action_input": arguments,
                "is_function_call": True
            }
            
            # 记录到历史（需要特殊格式）
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": message.function_call.arguments
                }
            })
        else:
            # LLM 直接回答（任务完成）
            answer = message.content
            result = {
                "thought": answer,
                "action": "finish",
                "action_input": None,
                "is_function_call": False
            }
            
            # 记录到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
        
        return result
    
    def _execute_action(self, action: str, action_input: Dict[str, Any]) -> str:
        """
        Action 阶段：执行函数调用
        
        设计要点：
        1. action_input 已经是字典，无需解析
        2. 直接调用对应的工具函数
        """
        if action == "finish":
            return "任务完成"
        
        # 查找工具
        if action not in self.tools:
            return f"错误：未知工具 '{action}'。可用工具：{', '.join(self.tools.keys())}"
        
        tool = self.tools[action]
        
        # 执行工具（action_input 已经是字典）
        try:
            # 根据函数参数调用
            if action == "calculate":
                result = tool(action_input.get("expression", ""))
            elif action == "search":
                result = tool(action_input.get("query", ""))
            else:
                # 通用调用
                result = tool(**action_input)
            
            return str(result)
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    
    def run(self, user_query: str) -> str:
        """
        运行 Agent 的主循环
        
        设计要点：
        1. 使用 Function Calling，无需正则解析
        2. 更可靠、更现代的实现
        """
        self.conversation_history = []
        observation = None
        
        print(f"\n{'='*50}")
        print(f"用户查询：{user_query}")
        print(f"{'='*50}\n")
        
        for iteration in range(self.max_iterations):
            print(f"[迭代 {iteration + 1}]")
            
            # Thought（使用 Function Calling）
            result = self._think(user_query, observation)
            thought = result["thought"]
            action = result["action"]
            action_input = result["action_input"]
            is_function_call = result["is_function_call"]
            
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            if action_input:
                print(f"Action Input: {action_input}")
            print()
            
            # Action
            if is_function_call:
                # action_input 已经是字典，直接使用
                observation = self._execute_action(action, action_input)
            else:
                # 任务完成
                observation = action_input if action_input else "任务完成"
            
            print(f"Observation: {observation}\n")
            
            # 将函数执行结果添加到历史
            if is_function_call:
                self.conversation_history.append({
                    "role": "function",
                    "name": action,
                    "content": observation
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
    
    agent = FunctionCallingAgent(api_key=api_key)
    
    # 测试示例
    agent.run("计算 123 + 456")

