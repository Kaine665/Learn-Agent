# 实践7：智能记账Agent

## 项目概述

这是一个综合性的智能记账Agent系统，整合了之前学到的所有Agent技术：
- ReAct循环（对话理解）
- 工具集成（文件解析、数据查询、统计分析）
- Plan-and-Execute（复杂查询分解）
- 记忆管理（用户偏好、历史查询、分析缓存）
- 反思机制（分析质量评估）
- 多Agent协作（数据录入、分析、报告生成）

## 核心功能

### 1. 数据录入
- **对话输入**：通过自然语言录入交易记录
  - "今天中午吃饭花了50元"
  - "1月15日，交通费30元，地铁"
  - "收入5000元，工资"
  
- **文件导入**：支持CSV和JSON格式
  ```python
  coordinator.process("导入文件", file_path="transactions.csv")
  ```

### 2. 历史流水展示
- 查看所有交易记录
- 按月份查询
- 按类别筛选
- 格式化展示

### 3. AI洞察分析
- **花销去向分析**：识别主要支出类别
- **趋势分析**：对比历史数据
- **异常发现**：识别大额支出和异常模式
- **优化建议**：提供节省开支的建议
- **每月可花销空间**：基于预算和当前支出计算

### 4. 预算管理
- 设置月度总预算
- 设置分类预算
- 实时计算剩余预算
- 预算使用情况分析

## 项目结构

```
practice7-accounting-agent/
├── models.py          # 数据模型（Transaction, Budget, UserPreference）
├── storage.py         # 数据存储层（JSON文件存储）
├── tools.py           # 工具系统（文件解析、查询、分析）
├── agents.py          # Agent系统（多Agent协作）
├── memory.py          # 记忆系统（短期和长期记忆）
├── example.py         # 示例程序
└── README.md          # 说明文档
```

## 架构设计

### 数据层
- **Transaction**：交易记录模型
- **Budget**：预算配置模型
- **UserPreference**：用户偏好模型
- **DataStorage**：数据存储管理（JSON文件）

### 工具层
- **FileParserTool**：文件解析（CSV、JSON、文本）
- **QueryTool**：数据查询和统计
- **AnalysisTool**：财务分析（预算计算、趋势分析、异常检测）

### Agent层
- **DataEntryAgent**：数据录入专家
  - 从对话提取交易信息
  - 处理文件导入
  
- **AnalystAgent**：财务分析专家
  - 花销去向分析
  - 趋势分析
  - 预算分析
  - AI洞察生成
  
- **ReporterAgent**：报告生成专家
  - 格式化展示历史流水
  - 生成统计报告
  
- **CoordinatorAgent**：协调者
  - 意图识别
  - Agent路由
  - 记忆管理
  - 结果整合

### 记忆层
- **ShortTermMemory**：当前对话上下文
- **LongTermMemory**：用户偏好、查询历史、分析缓存

## 使用方法

### 1. 环境准备

```bash
# 设置API Key
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key"

# Linux/Mac:
export OPENAI_API_KEY="your-api-key"
```

### 2. 运行示例

```bash
# 运行示例程序
python example.py

# 交互模式
python example.py interactive
```

### 3. 基本使用

```python
from storage import DataStorage
from agents import CoordinatorAgent
import os

# 初始化
api_key = os.getenv("OPENAI_API_KEY")
storage = DataStorage(data_dir="data")
coordinator = CoordinatorAgent(api_key=api_key, storage=storage)

# 录入数据
coordinator.process("今天中午吃饭花了50元")

# 查看流水
coordinator.process("显示我所有的交易记录")

# 分析花销
coordinator.process("分析一下我的花销去向")

# 导入文件
coordinator.process("导入文件", file_path="transactions.csv")
```

## 数据格式

### CSV文件格式

```csv
date,amount,category,description
2024-01-15,-50,餐饮,午餐
2024-01-15,-30,交通,地铁
2024-01-01,5000,收入,工资
```

### JSON文件格式

```json
[
  {
    "date": "2024-01-15",
    "amount": -50,
    "category": "餐饮",
    "description": "午餐"
  },
  {
    "date": "2024-01-15",
    "amount": -30,
    "category": "交通",
    "description": "地铁"
  }
]
```

## 设计亮点

### 1. 多Agent协作
- **专业化分工**：每个Agent专注于特定任务
- **智能路由**：Coordinator自动识别意图并路由到合适的Agent
- **上下文传递**：Agent之间可以共享上下文信息

### 2. 分层分析系统（AnalystAgent核心特性）
- **需求识别**：自动识别用户的分析需求类型（简单查询、分类分析、趋势分析、预算分析等）
- **按需获取数据**：根据分析需求只获取必要的数据，提高效率
- **动态生成分析**：根据用户具体问题生成针对性分析，而不是固定模板
  - 简单问题 → 直接回答数字
  - 分类问题 → 重点分析分类占比
  - 趋势问题 → 重点分析趋势变化
  - 预算问题 → 重点分析预算使用
  - 全面分析 → 提供完整报告

### 2. 记忆系统
- **短期记忆**：保持对话上下文，支持多轮对话
- **长期记忆**：记住用户偏好和历史查询
- **分析缓存**：缓存分析结果，提高响应速度

### 3. 工具系统
- **统一接口**：所有工具遵循相同的接口规范
- **可扩展性**：易于添加新工具
- **错误处理**：完善的异常处理机制

### 4. 数据存储
- **持久化**：JSON文件存储，数据不丢失
- **查询能力**：支持多条件查询
- **统计功能**：内置统计方法

## 扩展方向

### 1. 数据可视化
- 集成matplotlib或plotly生成图表
- 支出趋势图
- 分类占比饼图

### 2. 高级分析
- 预测未来支出
- 消费习惯分析
- 财务健康评分

### 3. 多用户支持
- 用户认证
- 数据隔离
- 共享账本

### 4. 移动端支持
- Web界面
- 移动App
- 语音输入

### 5. 集成外部服务
- 银行API对接
- 支付平台集成
- 发票识别（OCR）

## 学习要点

通过这个项目，你将深入理解：

1. **Agent系统设计**
   - 如何设计多Agent协作架构
   - 如何实现Agent间的通信和协调
   - 如何平衡专业化和通用性

2. **工具系统设计**
   - 如何设计统一的工具接口
   - 如何实现工具注册和调用机制
   - 如何处理工具执行错误

3. **记忆系统设计**
   - 如何区分短期和长期记忆
   - 如何设计记忆检索机制
   - 如何平衡记忆大小和性能

4. **数据模型设计**
   - 如何设计领域模型
   - 如何实现数据持久化
   - 如何设计查询接口

5. **实际应用开发**
   - 如何将Agent技术应用到实际问题
   - 如何整合多个技术组件
   - 如何设计用户友好的接口

## 常见问题

### Q: 如何添加新的分析功能？
A: 在`tools.py`中添加新的分析工具，然后在`AnalystAgent`中调用。

### Q: 如何支持更多文件格式？
A: 在`FileParserTool`中添加新的解析方法，并在`ToolRegistry`中注册。

### Q: 如何提高分析质量？
A: 可以改进Prompt设计，增加更多上下文信息，或者使用更强的模型。

### Q: 数据存储在哪里？
A: 默认存储在`data/`目录下，包括`transactions.json`、`budgets.json`、`preferences.json`和`memory.json`。

## 总结

这个项目展示了如何将Agent技术应用到实际场景中，整合了：
- ✅ ReAct循环
- ✅ 工具集成
- ✅ Plan-and-Execute
- ✅ 记忆管理
- ✅ 反思机制
- ✅ 多Agent协作

通过这个项目，你将具备设计和实现完整Agent系统的能力！

