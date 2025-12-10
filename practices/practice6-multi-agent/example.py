"""
实践6示例：运行多 Agent 协作系统
"""

import os
from agent import (
    CoordinatorAgent,
    ResearchAgent,
    AnalysisAgent,
    WriterAgent,
    ReviewerAgent
)


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 创建协调者
    coordinator = CoordinatorAgent(api_key=api_key)
    
    # 注册 Agent
    print("注册 Agent...")
    coordinator.register_agent(ResearchAgent(api_key=api_key))
    coordinator.register_agent(AnalysisAgent(api_key=api_key))
    coordinator.register_agent(WriterAgent(api_key=api_key))
    coordinator.register_agent(ReviewerAgent(api_key=api_key))
    print()
    
    # 示例1：研究写作任务
    print("\n" + "="*60)
    print("示例1：研究写作任务")
    print("="*60)
    
    coordinator.run("写一篇关于人工智能发展历史的文章")
    
    # 示例2：分析报告任务
    print("\n" + "="*60)
    print("示例2：分析报告任务")
    print("="*60)
    
    coordinator.run("分析 Python 编程语言的优势和劣势，并生成分析报告")


if __name__ == "__main__":
    main()

