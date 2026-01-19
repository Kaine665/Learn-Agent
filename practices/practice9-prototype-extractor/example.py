"""
原型提取统一入口示例

演示新架构的使用方式：
1. 完整流程：图片 → 布局提取 → HTML生成
2. 仅提取：图片 → PrototypeSpec
3. 仅生成：PrototypeSpec → HTML
"""

import argparse
import sys
import io

# Windows控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from orchestrator import PrototypeOrchestrator, extract_prototype, generate_prototype

def main():
    parser = argparse.ArgumentParser(description="原型提取工作流")
    parser.add_argument("-i", "--image", type=str, 
                        default="data/input-images/微信图片_20251223161332_45_42.jpg",
                        help="图片路径")
    parser.add_argument("-n", "--samples", type=int, default=3,
                        help="采样次数")
    parser.add_argument("--extract-only", action="store_true",
                        help="仅执行提取，不生成HTML")
    
    args = parser.parse_args()
    
    # 创建编排器
    orchestrator = PrototypeOrchestrator(
        sample_count=args.samples,
        max_retries=3
    )
    
    # 执行工作流
    state = orchestrator.run(
        image_path=args.image,
        skip_generation=args.extract_only
    )
    
    # 输出结果
    if state.error:
        print(f"\n❌ 失败: {state.error}")
        return 1
    
    if state.spec:
        print(f"\n📊 提取的规格:")
        print(f"   布局置信度: {state.spec.layout.confidence:.0%}")
        print(f"   区域数量: {len(state.spec.layout.regions)}")
    
    if state.html_path:
        print(f"\n🎨 HTML文件: {state.html_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

