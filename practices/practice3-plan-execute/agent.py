"""
实践3：Plan-and-Execute Agent

核心思想：理解规划与执行模式，解决长任务稳定性问题
"""

import re
from typing import List, Dict, Any, Optional
from openai import OpenAI


class PlanAndExecuteAgent:
    """
    Plan-and-Execute Agent
    
    设计要点：
    1. 两阶段架构：规划 + 执行
    2. 先规划整体任务，再逐步执行
    3. 支持计划调整
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.plan: List[str] = []
        self.execution_results: Dict[int, str] = {}  # 步骤编号 -> 执行结果
    
    def _build_planning_prompt(self, goal: str) -> str:
        """
        构建规划阶段的 Prompt
        
        设计要点：
        1. 明确告诉 LLM 要生成计划
        2. 要求输出格式化的计划
        3. 计划应该是可执行的步骤
        """
        return f"""你是一个任务规划专家。用户给你一个目标，你需要将其分解为可执行的步骤。

目标：{goal}

请将目标分解为具体的执行步骤，每个步骤应该：
1. 清晰明确
2. 可执行
3. 有明确的输出

请按照以下格式输出计划：

计划：
1. [第一步]
2. [第二步]
3. [第三步]
...

示例：
目标：写一篇关于 AI 的短文
计划：
1. 搜索 AI 的相关信息
2. 整理和筛选信息
3. 撰写文章大纲
4. 撰写文章正文
5. 检查和优化文章
"""
    
    def _build_execution_prompt(self, step: str, step_number: int, context: Dict[int, str]) -> str:
        """
        构建执行阶段的 Prompt
        
        设计要点：
        1. 提供当前步骤
        2. 提供之前步骤的执行结果（上下文）
        3. 要求执行当前步骤
        """
        context_str = ""
        if context:
            context_str = "\n\n之前步骤的执行结果：\n"
            for num, result in context.items():
                context_str += f"步骤 {num}: {result}\n"
        
        return f"""你是一个任务执行专家。请执行以下步骤：

当前步骤（步骤 {step_number}）：{step}
{context_str}

请执行这个步骤，并输出执行结果。如果步骤需要调用工具，请说明。
"""
    
    def plan(self, goal: str) -> List[str]:
        """
        规划阶段：生成任务计划
        
        设计要点：
        1. 使用 LLM 生成计划
        2. 解析计划为步骤列表
        3. 返回可执行的计划
        """
        print(f"\n{'='*50}")
        print("📋 规划阶段")
        print(f"{'='*50}\n")
        print(f"目标：{goal}\n")
        
        # 调用 LLM 生成计划
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个任务规划专家。"},
                {"role": "user", "content": self._build_planning_prompt(goal)}
            ],
            temperature=0.7
        )
        
        plan_output = response.choices[0].message.content
        print("生成的计划：")
        print(plan_output)
        print()
        
        # 解析计划
        self.plan = self._parse_plan(plan_output)
        
        print(f"✅ 计划生成完成，共 {len(self.plan)} 个步骤\n")
        return self.plan
    
    def _parse_plan(self, plan_text: str) -> List[str]:
        """
        解析计划文本，提取步骤列表
        
        设计要点：使用正则表达式提取编号的步骤
        """
        steps = []
        # 匹配 "1. xxx" 或 "步骤1: xxx" 格式
        pattern = r'(?:^|\n)\s*(?:\d+\.|步骤\s*\d+[:：])\s*(.+?)(?=\n\s*(?:\d+\.|步骤\s*\d+[:：])|$)'
        matches = re.findall(pattern, plan_text, re.MULTILINE)
        
        if matches:
            steps = [match.strip() for match in matches]
        else:
            # 如果没有匹配到，尝试按行分割
            lines = plan_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or '步骤' in line):
                    # 提取步骤内容
                    content = re.sub(r'^(?:\d+\.|步骤\s*\d+[:：])\s*', '', line)
                    if content:
                        steps.append(content)
        
        return steps if steps else ["执行任务"]
    
    def execute_step(self, step: str, step_number: int) -> str:
        """
        执行单个步骤
        
        设计要点：
        1. 使用 LLM 执行步骤
        2. 记录执行结果
        3. 返回执行结果
        """
        print(f"[步骤 {step_number}] {step}")
        
        # 构建上下文（之前步骤的结果）
        context = {num: result for num, result in self.execution_results.items() if num < step_number}
        
        # 调用 LLM 执行步骤
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个任务执行专家。"},
                {"role": "user", "content": self._build_execution_prompt(step, step_number, context)}
            ],
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        self.execution_results[step_number] = result
        
        print(f"执行结果：{result}\n")
        return result
    
    def execute(self, goal: str) -> str:
        """
        执行阶段：按计划逐步执行
        
        设计要点：
        1. 先规划
        2. 再执行每个步骤
        3. 最后汇总结果
        """
        # 1. 规划
        plan = self.plan(goal)
        
        if not plan:
            return "错误：无法生成计划"
        
        # 2. 执行
        print(f"\n{'='*50}")
        print("⚙️ 执行阶段")
        print(f"{'='*50}\n")
        
        for i, step in enumerate(plan, 1):
            result = self.execute_step(step, i)
            self.execution_results[i] = result
        
        # 3. 汇总
        print(f"\n{'='*50}")
        print("✅ 执行完成")
        print(f"{'='*50}\n")
        
        summary = self._generate_summary(goal)
        return summary
    
    def _generate_summary(self, goal: str) -> str:
        """生成执行总结"""
        summary = f"任务目标：{goal}\n\n"
        summary += "执行结果：\n"
        for step_num, result in self.execution_results.items():
            summary += f"步骤 {step_num}: {result}\n"
        return summary
    
    def run(self, goal: str) -> str:
        """
        运行 Agent（规划 + 执行）
        
        设计要点：这是 Plan-and-Execute 模式的完整流程
        """
        return self.execute(goal)


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        exit(1)
    
    agent = PlanAndExecuteAgent(api_key=api_key)
    agent.run("写一篇关于 AI 的短文")

