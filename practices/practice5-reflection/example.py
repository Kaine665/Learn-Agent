"""
实践5示例：运行反思机制 Agent
"""

import os
from agent import ReflectionAgent


def simple_text_generator(topic: str) -> str:
    """简单的文本生成器（模拟）"""
    return f"关于{topic}的文章。{topic}是一个重要的话题。我们需要关注{topic}的发展。"


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    agent = ReflectionAgent(api_key=api_key)
    
    # 示例1：文本生成任务（会进行反思和优化）
    print("\n" + "="*60)
    print("示例1：文本生成任务（带反思）")
    print("="*60)
    
    agent.run(
        goal="生成一篇关于人工智能的高质量文章，要求内容丰富、结构清晰",
        action_func=simple_text_generator,
        topic="人工智能"
    )
    
    # 示例2：错误恢复
    print("\n" + "="*60)
    print("示例2：错误恢复")
    print("="*60)
    
    def unreliable_action():
        """模拟可能失败的行动"""
        import random
        if random.random() < 0.5:
            raise Exception("网络错误：连接超时")
        return "执行成功"
    
    try:
        agent.run(
            goal="执行一个可能失败的任务",
            action_func=unreliable_action
        )
    except Exception as e:
        print(f"最终错误：{e}")


if __name__ == "__main__":
    main()

