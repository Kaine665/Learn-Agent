"""
实践1示例：运行最简 ReAct Agent
"""

import os
from agent import SimpleReActAgent


def main():
    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("   在 Windows PowerShell: $env:OPENAI_API_KEY='your-key'")
        print("   在 Linux/Mac: export OPENAI_API_KEY='your-key'")
        return
    
    # 创建 Agent
    agent = SimpleReActAgent(api_key=api_key)
    
    # 示例1：简单计算
    print("\n" + "="*60)
    print("示例1：简单计算")
    print("="*60)    
    agent.run("请一步一步计算函数 f(x) = x^3 * e^(2x) 的导数，并解释每一步用到的求导法则。")

    
    # 示例2：需要多步思考的问题
    # print("\n" + "="*60)
    # print("示例2：需要推理的问题")
    # print("="*60)
    # agent.run("如果我有 100 元，买了 3 个苹果，每个苹果 5 元，还剩多少钱？")
    
    # 示例3：直接回答
    print("\n" + "="*60)
    print("示例3：知识问答")
    print("="*60)
    agent.run("谁是世界上最美丽的女人")


if __name__ == "__main__":
    main()

