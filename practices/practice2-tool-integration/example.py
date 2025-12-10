"""
实践2示例：运行工具集成 Agent
"""

import os
from agent import ToolIntegratedAgent


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 创建 Agent
    agent = ToolIntegratedAgent(api_key=api_key)
    
    # 示例1：使用计算器工具
    print("\n" + "="*60)
    print("示例1：使用计算器工具")
    print("="*60)
    agent.run("计算 123 * 456")
    
    # 示例2：使用搜索工具
    print("\n" + "="*60)
    print("示例2：使用搜索工具")
    print("="*60)
    agent.run("搜索 Python 教程")
    
    # 示例3：复杂任务（需要多步）
    print("\n" + "="*60)
    print("示例3：复杂任务")
    print("="*60)
    agent.run("先计算 100 * 2，然后搜索这个结果的相关信息")


if __name__ == "__main__":
    main()

