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
    
    # 示例1：使用计算器工具
    print("\n" + "="*60)
    print("示例1：使用计算器工具（Function Calling）")
    print("="*60)
    agent.run("计算 123 * 456")
    
    # 示例2：使用搜索工具
    print("\n" + "="*60)
    print("示例2：使用搜索工具（Function Calling）")
    print("="*60)
    agent.run("搜索 Python 教程")
    
    # 示例3：复杂任务
    print("\n" + "="*60)
    print("示例3：复杂任务（多步 Function Calling）")
    print("="*60)
    agent.run("先计算 100 * 2，然后搜索这个结果的相关信息")


if __name__ == "__main__":
    main()

