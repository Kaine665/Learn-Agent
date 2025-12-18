"""
小红书帖子阅读Agent示例程序
"""

import os
from dotenv import load_dotenv
from rednote_agent import RednoteReadingAgent

# 加载环境变量
load_dotenv()

def main():
    """主函数"""
    # 获取API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("   方式1：在 .env 文件中设置")
        print("   方式2：使用 export OPENAI_API_KEY=your_key")
        return
    
    # 创建Agent
    agent = RednoteReadingAgent(api_key=api_key)
    
    print("=" * 60)
    print("📚 小红书帖子阅读管家")
    print("=" * 60)
    print("\n功能说明：")
    print("1. 添加帖子：输入小红书URL，例如：")
    print("   '获取这个帖子：https://www.xiaohongshu.com/explore/...'")
    print("2. 总结帖子：'总结所有未读帖子' 或 '总结帖子 post_xxx'")
    print("3. 查看列表：'列出所有帖子'")
    print("4. 查看状态：'阅读状态'")
    print("5. 批量批阅：'批量批阅'")
    print("6. 退出：输入 'quit' 或 'exit'")
    print("\n" + "=" * 60)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n💬 你：").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n👋 再见！")
                break
            
            # 处理用户输入
            response = agent.process(user_input)
            print(f"\n🤖 管家：{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误：{e}")


if __name__ == "__main__":
    main()

