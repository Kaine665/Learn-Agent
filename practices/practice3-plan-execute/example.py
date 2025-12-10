"""
实践3示例：运行 Plan-and-Execute Agent
"""

import os
from agent import PlanAndExecuteAgent


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    agent = PlanAndExecuteAgent(api_key=api_key)
    
    # 示例1：写作任务
    print("\n" + "="*60)
    print("示例1：写作任务")
    print("="*60)
    agent.run("写一篇关于 Python 编程的短文")
    
    # 示例2：研究任务
    print("\n" + "="*60)
    print("示例2：研究任务")
    print("="*60)
    agent.run("分析人工智能的发展历史，并总结主要里程碑")


if __name__ == "__main__":
    main()

