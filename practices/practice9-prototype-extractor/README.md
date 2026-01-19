# 原型提取工作流

这是一个基于视觉模型的原型提取和生成系统，能够从UI原型图片中自动提取布局结构并生成对应的HTML代码。

## 系统架构

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  example.py                                              │ │
│  │  命令行入口，解析参数，调用编排器                           │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        编排层                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  orchestrator.py                                         │ │
│  │  PrototypeOrchestrator - 工作流编排，状态管理              │ │
│  │  ├─ run()           完整流程执行                          │ │
│  │  ├─ extract_only()  仅提取                               │ │
│  │  └─ generate_only() 仅生成                               │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        能力层                                │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │  extractors/         │    │  generators/         │       │
│  │  ├─ BaseExtractor    │    │  └─ HTMLGenerator    │       │
│  │  │   多次采样+合并    │    │      HTML代码生成    │       │
│  │  │   重试机制        │    │                      │       │
│  │  │   进度追踪        │    │                      │       │
│  │  └─ LayoutExtractor  │    │                      │       │
│  │      布局分析实现     │    │                      │       │
│  └──────────────────────┘    └──────────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                        数据层                                │
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │  specs/              │    │  prompts/            │       │
│  │  ├─ PrototypeSpec    │    │  ├─ prompts.json     │       │
│  │  ├─ LayoutSpec       │    │  ├─ layout_analysis  │       │
│  │  ├─ RegionSpec       │    │  └─ prototype_gen    │       │
│  │  └─ ComponentSpec    │    │                      │       │
│  └──────────────────────┘    └──────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
                    ┌─────────────┐
                    │   图片输入   │
                    └──────┬──────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    LayoutExtractor                           │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                     │
│  │ 采样 1  │   │ 采样 2  │   │ 采样 3  │  并行调用 GPT-4o    │
│  └────┬────┘   └────┬────┘   └────┬────┘                     │
│       │             │             │                          │
│       └─────────────┼─────────────┘                          │
│                     ▼                                        │
│              ┌─────────────┐                                 │
│              │  LLM 合并   │  分析差异，选择最优              │
│              └──────┬──────┘                                 │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       ▼
                ┌─────────────┐
                │ LayoutSpec  │  结构化数据
                └──────┬──────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    HTMLGenerator                             │
│                                                              │
│   LayoutSpec  ──→  Prompt  ──→  GPT-4o  ──→  HTML代码        │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
                ┌─────────────┐
                │  HTML文件   │  Tailwind CSS + shadcn/ui
                └─────────────┘
```

### 核心设计

1. **多次采样 + 智能合并**
   - 对同一图片进行多次分析（默认3次）
   - 通过LLM分析各次结果的差异
   - 智能选择最合理的描述，提高准确性

2. **分层解耦**
   - 编排层：负责流程控制和状态管理
   - 能力层：专注单一能力实现
   - 数据层：统一的数据结构定义

3. **可扩展性**
   - 新增提取器：继承 `BaseExtractor`，实现 `_extract_once()` 和 `_merge_samples()`
   - 新增生成器：参考 `HTMLGenerator` 实现模式

## 使用方法

### 1. 完整工作流

```python
from orchestrator import PrototypeOrchestrator

# 创建编排器
orchestrator = PrototypeOrchestrator(sample_count=3)

# 执行完整流程：提取 + 生成
state = orchestrator.run(image_path="your_prototype.png")
print(f"HTML文件已生成: {state.html_path}")
```

### 2. 仅提取布局

```python
from orchestrator import extract_prototype

# 仅提取布局规格
spec = extract_prototype("your_prototype.png", sample_count=3)
print(f"置信度: {spec.layout.confidence:.0%}")
```

### 3. 仅生成HTML

```python
from orchestrator import generate_prototype

# 从图片直接生成HTML
html_path = generate_prototype("your_prototype.png", sample_count=3)
print(f"HTML文件: {html_path}")
```

### 4. 命令行使用

```bash
# 完整流程（默认3次采样）
python example.py

# 指定图片和采样次数
python example.py -i your_image.png -n 5

# 仅提取，不生成HTML
python example.py -i your_image.png --extract-only
```

## 目录结构

```
├── data/                    # 数据目录
│   ├── input-images/        # 输入图片
│   ├── extraction-logs/     # 提取过程日志
│   └── prototypes/          # 生成的HTML原型
├── specs/                   # 数据规格定义
├── extractors/              # 提取器实现
├── generators/              # 生成器实现
├── prompts/                 # 提示词模板
├── example.py               # 使用示例
└── orchestrator.py          # 工作流编排器
```

## 依赖项

- langchain-openai
- python-dotenv
- pillow (用于图片处理)

## 环境变量

创建 `.env` 文件并设置：

```
OPENAI_API_KEY=your_api_key_here
```

## 输出格式

- **布局规格**: 结构化JSON，包含设备信息、区域划分、组件识别等
- **HTML原型**: 使用Tailwind CSS + shadcn/ui的响应式页面
- **分析记录**: 保存到record目录的TXT文件，包含完整分析过程