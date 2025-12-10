"""
实践4示例：运行带记忆的 Agent
"""

import os
from agent import AgentWithMemory


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    agent = AgentWithMemory(api_key=api_key)
    
    # 示例1：多轮对话（短期记忆）
    print("\n" + "="*60)
    print("示例1：多轮对话（测试短期记忆）")
    print("="*60)
    
    agent.run("我的名字是张三")
    agent.run("我今年25岁")
    agent.run("我的名字是什么？")  # Agent 应该记住名字
    agent.run("我多大了？")  # Agent 应该记住年龄
    
    # 示例2：长期记忆
    print("\n" + "="*60)
    print("示例2：长期记忆")
    print("="*60)
    
    agent.run("记住我的偏好：我喜欢在早上喝咖啡")
    agent.run("记住我的偏好：我不喜欢甜食")
    
    # 清空短期记忆，但长期记忆保留
    agent.stm.clear()
    
    agent.run("我早上应该喝什么？")  # Agent 应该从长期记忆中找到偏好
    
    # 显示记忆统计
    stats = agent.get_memory_stats()
    print(f"\n记忆统计：")
    print(f"  短期记忆轮数：{stats['short_term_turns']}")
    print(f"  长期记忆项数：{stats['long_term_items']}")


if __name__ == "__main__":
    main()

