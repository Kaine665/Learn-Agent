"""
实践1.1示例：运行 Function Calling Agent
"""

import os
from agent import FunctionCallingAgent


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("   在 Windows PowerShell: $env:OPENAI_API_KEY='your-key'")
        print("   在 Linux/Mac: export OPENAI_API_KEY='your-key'")
        return
    
    # 创建 Agent
    agent = FunctionCallingAgent(api_key=api_key)
    

    # 示例1：简单计算
    print("\n" + "="*60)
    print("示例1：数学计算")
    print("="*60)    
    agent.run("请一步一步计算函数 f(x) = x^3 * e^(2x) 的导数，并解释每一步用到的求导法则。")


    # 示例2：知识问答
    print("\n" + "="*60)
    print("示例2：知识问答")
    print("="*60)
    agent.run("谁是世界上最美丽的女人")

    # 示例3：软件制作
    print("\n" + "="*60)
    print("示例3：软件制作")
    print("="*60)
    agent.run("帮我写一个全栈安卓软件，用来记账并且AI洞察你的消费习惯")

if __name__ == "__main__":
    main()

