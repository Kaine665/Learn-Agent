"""
记账Agent示例程序
"""

import os
from storage import DataStorage
from agents import CoordinatorAgent
from models import Transaction, Budget


def main():
    """主函数"""
    # 检查API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("Windows PowerShell: $env:OPENAI_API_KEY=\"your-api-key\"")
        return
    
    # 初始化
    print("🚀 初始化记账Agent...")
    storage = DataStorage(data_dir="data")
    coordinator = CoordinatorAgent(api_key=api_key, storage=storage)
    
    print("✅ 初始化完成！\n")
    
    # 示例1：通过对话录入数据
    print("=" * 60)
    print("示例1：通过对话录入交易记录")
    print("=" * 60)
    coordinator.process("今天中午吃饭花了50元，类别是餐饮")
    coordinator.process("1月15日，交通费30元，地铁")
    coordinator.process("收入5000元，工资，类别是收入")
    
    # 示例2：查看历史流水
    print("\n" + "=" * 60)
    print("示例2：查看历史流水")
    print("=" * 60)
    coordinator.process("显示我所有的交易记录")
    coordinator.process("查看1月份的流水")
    
    # 示例3：分析花销
    print("\n" + "=" * 60)
    print("示例3：分析花销去向")
    print("=" * 60)
    coordinator.process("分析一下我的花销去向")
    coordinator.process("这个月我还能花多少钱？")
    
    # 示例4：设置预算
    print("\n" + "=" * 60)
    print("示例4：设置预算")
    print("=" * 60)
    budget = Budget(
        month="2024-01",
        total_budget=5000,
        category_budgets={
            "餐饮": 1000,
            "交通": 500,
            "购物": 2000
        }
    )
    storage.set_budget(budget)
    print(f"✅ 已设置 {budget.month} 的预算：总预算 {budget.total_budget} 元")
    
    # 示例5：预算分析
    print("\n" + "=" * 60)
    print("示例5：预算分析")
    print("=" * 60)
    coordinator.process("分析一下我的预算使用情况")
    coordinator.process("1月份我还剩多少预算？")


def interactive_mode():
    """交互模式"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    storage = DataStorage(data_dir="data")
    coordinator = CoordinatorAgent(api_key=api_key, storage=storage)
    
    # 显示当前数据状态
    transaction_count = len(storage.transactions)
    print("\n" + "=" * 60)
    print("📊 数据加载状态")
    print("=" * 60)
    
    if transaction_count > 0:
        print(f"✅ 已加载 {transaction_count} 条交易记录")
        
        # 显示日期范围
        dates = [t.date for t in storage.transactions]
        print(f"📅 日期范围：{min(dates)} 至 {max(dates)}")
        
        # 显示基本统计
        total_income = storage.get_total_income()
        total_expense = storage.get_total_expense()
        balance = total_income - total_expense
        
        print(f"💰 总收入：{total_income:.2f} 元")
        print(f"💸 总支出：{total_expense:.2f} 元")
        print(f"💵 结余：{balance:.2f} 元")
        
        # 显示最近的几条记录
        print(f"\n📋 最近5条交易记录：")
        for i, t in enumerate(storage.transactions[:5], 1):
            amount_str = f"{t.amount:+.2f}"
            print(f"  {i}. {t.date} | {t.category:<8} | {amount_str:>10} | {t.description}")
        
        if transaction_count > 5:
            print(f"  ... 还有 {transaction_count - 5} 条记录")
    else:
        print("📝 当前没有交易记录")
        print("💡 你可以通过以下方式添加数据：")
        print("   - 对话录入：'今天中午吃饭花了50元'")
        print("   - 导入文件：'file:微信支付账单流水.xlsx'")
    
    print("\n" + "=" * 60)
    print("记账Agent - 交互模式")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'file:<路径>' 导入文件（数据会持久化保存）")
    print("=" * 60 + "\n")
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            # 处理文件导入
            if user_input.startswith('file:'):
                file_path = user_input[5:].strip()
                # 去掉可能的 <> 符号
                file_path = file_path.strip('<>').strip('"').strip("'")
                coordinator.process("导入文件", file_path=file_path)
            else:
                coordinator.process(user_input)
        
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误：{str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        main()

