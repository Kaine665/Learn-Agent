"""
实践5：反思机制 Agent

核心思想：理解自我评估、错误恢复和结果优化
"""

from typing import Dict, Any, Optional, List
from openai import OpenAI
import re


class ReflectionAgent:
    """
    带反思机制的 Agent
    
    设计要点：
    1. 执行后反思
    2. 错误恢复
    3. 结果优化
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_reflections = 3  # 最大反思次数，避免无限循环
        self.execution_history: List[Dict] = []
    
    def _build_reflection_prompt(self, goal: str, action: str, result: str) -> str:
        """
        构建反思 Prompt
        
        设计要点：
        1. 提供目标和执行结果
        2. 要求评估结果质量
        3. 提供改进建议
        """
        return f"""你是一个反思专家。请评估以下执行结果：

目标：{goal}
执行行动：{action}
执行结果：{result}

请评估：
1. 结果是否满足目标？
2. 结果有什么问题？
3. 如何改进？

请按照以下格式输出：

评估：满意/不满意
问题：[列出问题]
改进建议：[列出改进建议]
"""
    
    def reflect(self, goal: str, action: str, result: str) -> Dict[str, Any]:
        """
        反思阶段：评估执行结果
        
        设计要点：
        1. 使用 LLM 评估结果
        2. 提取评估、问题和建议
        3. 返回结构化反思结果
        """
        prompt = self._build_reflection_prompt(goal, action, result)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个反思专家，能够评估执行结果并提供改进建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # 降低温度，让反思更稳定
        )
        
        reflection_output = response.choices[0].message.content
        
        # 解析反思结果
        return self._parse_reflection(reflection_output)
    
    def _parse_reflection(self, reflection_text: str) -> Dict[str, Any]:
        """解析反思结果"""
        # 提取评估
        assessment_match = re.search(r'评估[：:]\s*(满意|不满意)', reflection_text)
        is_satisfied = assessment_match.group(1) == "满意" if assessment_match else False
        
        # 提取问题
        problem_match = re.search(r'问题[：:]\s*(.+?)(?=\n改进建议|$)', reflection_text, re.DOTALL)
        problems = problem_match.group(1).strip() if problem_match else ""
        
        # 提取改进建议
        improvement_match = re.search(r'改进建议[：:]\s*(.+?)$', reflection_text, re.DOTALL)
        improvements = improvement_match.group(1).strip() if improvement_match else ""
        
        return {
            "is_satisfied": is_satisfied,
            "problems": problems,
            "improvements": improvements,
            "raw": reflection_text
        }
    
    def _build_improvement_prompt(self, goal: str, initial_result: str, critique: Dict[str, Any]) -> str:
        """
        构建改进 Prompt
        
        设计要点：
        1. 提供初始结果和反思意见
        2. 要求生成改进后的结果
        """
        return f"""你是一个优化专家。请根据反思意见改进结果。

目标：{goal}
初始结果：{initial_result}

反思意见：
问题：{critique['problems']}
改进建议：{critique['improvements']}

请生成改进后的结果。
"""
    
    def refine(self, goal: str, initial_result: str, critique: Dict[str, Any]) -> str:
        """
        结果优化：根据反思意见优化结果
        
        设计要点：
        1. 使用 LLM 根据反思意见优化
        2. 生成改进后的结果
        """
        prompt = self._build_improvement_prompt(goal, initial_result, critique)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个优化专家，能够根据反思意见改进结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        错误恢复：根据错误类型决定恢复策略
        
        设计要点：
        1. 分析错误类型
        2. 选择恢复策略
        3. 返回恢复建议
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 简单的错误分类和恢复策略
        recovery_strategies = {
            "网络错误": "重试操作",
            "参数错误": "检查并调整参数",
            "权限错误": "检查权限设置",
            "超时错误": "增加超时时间或重试"
        }
        
        # 使用 LLM 分析错误并给出恢复建议
        error_prompt = f"""执行过程中发生错误：

错误类型：{error_type}
错误信息：{error_msg}
上下文：{context}

请分析错误原因，并给出恢复策略。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个错误处理专家。"},
                {"role": "user", "content": error_prompt}
            ],
            temperature=0.3
        )
        
        recovery_advice = response.choices[0].message.content
        
        return {
            "error_type": error_type,
            "error_msg": error_msg,
            "recovery_advice": recovery_advice,
            "should_retry": "重试" in recovery_advice or "retry" in recovery_advice.lower()
        }
    
    def execute_with_reflection(self, goal: str, action_func, *args, **kwargs) -> str:
        """
        带反思的执行流程
        
        设计要点：
        1. 执行行动
        2. 反思结果
        3. 如果不满意，优化并重试
        4. 记录执行历史
        """
        print(f"\n{'='*50}")
        print(f"目标：{goal}")
        print(f"{'='*50}\n")
        
        best_result = None
        reflection_count = 0
        
        for iteration in range(self.max_reflections + 1):
            print(f"[执行 {iteration + 1}]")
            
            try:
                # 1. 执行行动
                if iteration == 0:
                    result = action_func(*args, **kwargs)
                else:
                    # 使用改进后的参数重试
                    result = action_func(*args, **kwargs)
                
                print(f"执行结果：{result}\n")
                
                # 2. 反思
                reflection = self.reflect(goal, str(action_func), result)
                
                print(f"反思结果：")
                print(f"  评估：{'✅ 满意' if reflection['is_satisfied'] else '❌ 不满意'}")
                if reflection['problems']:
                    print(f"  问题：{reflection['problems']}")
                if reflection['improvements']:
                    print(f"  改进建议：{reflection['improvements']}")
                print()
                
                # 3. 记录历史
                self.execution_history.append({
                    "iteration": iteration + 1,
                    "result": result,
                    "reflection": reflection
                })
                
                # 4. 如果满意，返回结果
                if reflection['is_satisfied']:
                    print("✅ 结果满意，任务完成！")
                    return result
                
                # 5. 如果不满意且还有机会，优化结果
                if iteration < self.max_reflections:
                    print(f"[优化 {iteration + 1}]")
                    result = self.refine(goal, result, reflection)
                    print(f"优化后结果：{result}\n")
                    best_result = result
                    reflection_count += 1
                else:
                    best_result = result
                    break
                    
            except Exception as e:
                # 错误恢复
                print(f"❌ 执行错误：{e}")
                recovery = self.handle_error(e, {"goal": goal, "args": args, "kwargs": kwargs})
                print(f"恢复建议：{recovery['recovery_advice']}\n")
                
                if recovery['should_retry'] and iteration < self.max_reflections:
                    print("🔄 尝试恢复...")
                    continue
                else:
                    raise
        
        print(f"⚠️ 达到最大反思次数（{self.max_reflections}），返回当前最佳结果")
        return best_result
    
    def run(self, goal: str, action_func, *args, **kwargs) -> str:
        """
        运行 Agent（带反思）
        
        设计要点：这是反思循环的完整实现
        """
        return self.execute_with_reflection(goal, action_func, *args, **kwargs)


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    agent = ReflectionAgent(api_key=api_key)
    
    # 示例：简单的文本生成任务
    def generate_text(topic: str) -> str:
        """模拟文本生成"""
        return f"这是一篇关于{topic}的文章。文章内容..."
    
    agent.run("生成一篇高质量的文章", generate_text, "人工智能")

