# Agent 反思与错误处理标准

## 核心原则

> **反思机制和错误处理必须具有可见性和可解释性，让用户能够清楚地看到 Agent 做了什么、为什么这样做。**

---

## 一、反思机制的标准

### 1.1 反思评估标准

**❌ 不好的做法：**
- 只有"满意/不满意"的二元判断
- 没有量化评估
- 无法对比优化前后的差异

**✅ 好的做法：**
- 提供具体的问题分析
- 给出明确的改进建议
- 记录反思过程，便于追溯

### 1.2 反思 Prompt 设计标准

```python
def _build_reflection_prompt(self, goal: str, action: str, result: str) -> str:
    """
    反思 Prompt 应该包含：
    1. 明确的目标
    2. 执行行动
    3. 执行结果
    4. 评估要求（问题、改进建议）
    """
    return f"""你是一个反思专家。请评估以下执行结果：

目标：{goal}
执行行动：{action}
执行结果：{result}

请评估：
1. 结果是否满足目标？
2. 结果有什么问题？
3. 如何改进？

请按照以下格式输出：

评估：满意/不满意
问题：[列出问题]
改进建议：[列出改进建议]
"""
```

---

## 二、结果优化的标准

### 2.1 改动追踪标准

**核心要求：必须说明改了什么、为什么改**

**❌ 不好的做法：**
```python
# 只返回优化后的结果，没有改动说明
def refine(self, goal, initial_result, critique):
    return optimized_result  # 用户不知道改了什么
```

**✅ 好的做法：**
```python
# 返回优化结果和改动说明
def refine(self, goal, initial_result, critique) -> Dict[str, Any]:
    """
    返回：
    - optimized_result: 优化后的结果
    - changes: 改动说明列表
    """
    return {
        "optimized_result": optimized_result,
        "changes": [
            "开头部分：原为'简单介绍' → 改为'详细引言'，原因：增加文章深度",
            "结构部分：添加了段落标题，原因：提高可读性"
        ]
    }
```

### 2.2 优化 Prompt 设计标准

```python
def _build_improvement_prompt(self, goal: str, initial_result: str, critique: Dict[str, Any]) -> str:
    """
    优化 Prompt 必须要求：
    1. 生成改进后的结果
    2. 详细说明改动位置和原因
    """
    return f"""你是一个优化专家。请根据反思意见改进结果。

目标：{goal}
初始结果：{initial_result}

反思意见：
问题：{critique['problems']}
改进建议：{critique['improvements']}

请生成改进后的结果，并详细说明你做了哪些改动以及为什么改动。

请按照以下格式输出：

改进后的结果：
[改进后的完整结果]

改动说明：
1. [改动位置/内容]：原为"[原文片段]" → 改为"[新文片段]"，原因：[为什么改动]
2. [改动位置/内容]：原为"[原文片段]" → 改为"[新文片段]"，原因：[为什么改动]
...
"""
```

### 2.3 改动说明解析标准

```python
def _parse_refinement_output(self, output: str) -> Dict[str, Any]:
    """
    解析优化输出，提取：
    1. 改进后的结果
    2. 改动说明列表
    
    解析策略：
    - 使用正则表达式提取结构化内容
    - 支持多种格式（数字编号、符号列表）
    - 容错处理：如果格式不匹配，尝试提取包含关键词的行
    """
    # 提取改进后的结果
    result_match = re.search(r'改进后的结果[：:]\s*(.+?)(?=\n改动说明|$)', output, re.DOTALL)
    optimized_result = result_match.group(1).strip() if result_match else output
    
    # 提取改动说明
    changes_match = re.search(r'改动说明[：:]\s*(.+?)$', output, re.DOTALL)
    changes_text = changes_match.group(1).strip() if changes_match else ""
    
    # 解析改动列表
    changes = []
    if changes_text:
        for line in changes_text.split('\n'):
            line = line.strip()
            # 匹配以数字开头或-开头的行
            if line and (line[0].isdigit() or line.startswith('-')):
                change_desc = re.sub(r'^\d+[\.、]\s*|- ', '', line)
                if change_desc:
                    changes.append(change_desc)
            # 容错：提取包含关键词的行
            elif line and ('原为' in line or '改为' in line or '原因' in line):
                changes.append(line)
    
    return {
        "optimized_result": optimized_result,
        "changes": changes,
        "raw": output
    }
```

### 2.4 改动说明显示标准

```python
# 在执行流程中显示改动说明
if changes:
    print(f"📝 改动说明：")
    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change}")
    print()
else:
    print("📝 改动说明：无详细改动说明\n")
```

**显示效果示例：**
```
📝 改动说明：
  1. 开头部分：原为"关于人工智能的文章" → 改为"人工智能：变革时代的引擎"，原因：增加吸引力和专业性
  2. 结构部分：添加了"引言"、"主体"、"结论"三个部分，原因：提高文章结构清晰度
  3. 内容部分：原为"简单介绍" → 改为"详细阐述定义、应用、挑战"，原因：增加内容深度和丰富度
```

---

## 三、错误处理的标准

### 3.1 错误分析可见性标准

**核心要求：必须说明错误原因、影响、恢复策略**

**❌ 不好的做法：**
```python
# 只返回简单的恢复建议
def handle_error(self, error, context):
    return {
        "recovery_advice": "重试操作",  # 用户不知道为什么重试
        "should_retry": True
    }
```

**✅ 好的做法：**
```python
# 返回详细的错误分析
def handle_error(self, error, context) -> Dict[str, Any]:
    """
    返回：
    - reason: 错误原因分析
    - impact: 错误影响
    - possible_causes: 可能原因
    - recovery_strategy: 恢复策略
    - prevention: 预防措施
    - should_retry: 是否应该重试
    """
    return {
        "error_type": error_type,
        "error_msg": error_msg,
        "reason": "网络连接超时，可能是网络不稳定或服务器响应慢",
        "impact": "无法获取数据，任务无法继续",
        "possible_causes": ["网络不稳定", "服务器负载高", "超时设置过短"],
        "recovery_strategy": "增加超时时间并重试，最多重试3次",
        "prevention": "设置合理的超时时间，添加重试机制",
        "should_retry": True
    }
```

### 3.2 错误分析 Prompt 设计标准

```python
def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    错误分析 Prompt 必须要求：
    1. 详细分析错误原因
    2. 说明错误影响
    3. 列出可能原因
    4. 提供恢复策略
    5. 给出预防措施
    6. 明确是否应该重试
    """
    error_prompt = f"""执行过程中发生错误：

错误类型：{error_type}
错误信息：{error_msg}
上下文：{context}

请详细分析：
1. 错误原因：为什么会发生这个错误？
2. 错误影响：这个错误对任务有什么影响？
3. 可能原因：可能的原因有哪些？
4. 恢复策略：应该采取什么策略来恢复？
5. 预防措施：如何避免再次发生？

请按照以下格式输出：

错误分析：
原因：[详细分析错误原因]
影响：[说明错误的影响]
可能原因：[列出可能的原因]
恢复策略：[具体的恢复策略]
预防措施：[如何预防]

是否应该重试：是/否
"""
```

### 3.3 错误分析解析标准

```python
def _parse_error_analysis(self, analysis_text: str, error_type: str, error_msg: str) -> Dict[str, Any]:
    """
    解析错误分析结果，提取：
    1. 错误原因
    2. 错误影响
    3. 可能原因
    4. 恢复策略
    5. 预防措施
    6. 是否应该重试
    """
    reason_match = re.search(r'原因[：:]\s*(.+?)(?=\n影响|$)', analysis_text, re.DOTALL)
    impact_match = re.search(r'影响[：:]\s*(.+?)(?=\n可能原因|$)', analysis_text, re.DOTALL)
    possible_causes_match = re.search(r'可能原因[：:]\s*(.+?)(?=\n恢复策略|$)', analysis_text, re.DOTALL)
    recovery_match = re.search(r'恢复策略[：:]\s*(.+?)(?=\n预防措施|$)', analysis_text, re.DOTALL)
    prevention_match = re.search(r'预防措施[：:]\s*(.+?)(?=\n是否应该重试|$)', analysis_text, re.DOTALL)
    retry_match = re.search(r'是否应该重试[：:]\s*(是|否)', analysis_text)
    
    return {
        "error_type": error_type,
        "error_msg": error_msg,
        "reason": reason_match.group(1).strip() if reason_match else "",
        "impact": impact_match.group(1).strip() if impact_match else "",
        "possible_causes": possible_causes_match.group(1).strip() if possible_causes_match else "",
        "recovery_strategy": recovery_match.group(1).strip() if recovery_match else "",
        "prevention": prevention_match.group(1).strip() if prevention_match else "",
        "should_retry": retry_match.group(1) == "是" if retry_match else False,
        "raw": analysis_text
    }
```

### 3.4 错误分析显示标准

```python
# 在执行流程中显示错误分析
print(f"\n🔍 错误分析：")
if recovery.get("reason"):
    print(f"  原因：{recovery['reason']}")
if recovery.get("impact"):
    print(f"  影响：{recovery['impact']}")
if recovery.get("possible_causes"):
    print(f"  可能原因：{recovery['possible_causes']}")
if recovery.get("recovery_strategy"):
    print(f"  恢复策略：{recovery['recovery_strategy']}")
if recovery.get("prevention"):
    print(f"  预防措施：{recovery['prevention']}")
print(f"  是否重试：{'✅ 是' if recovery['should_retry'] else '❌ 否'}\n")
```

**显示效果示例：**
```
🔍 错误分析：
  原因：网络连接超时，可能是网络不稳定或服务器响应慢
  影响：无法获取数据，任务无法继续
  可能原因：网络不稳定、服务器负载高、超时设置过短
  恢复策略：增加超时时间并重试，最多重试3次
  预防措施：设置合理的超时时间，添加重试机制
  是否重试：✅ 是
```

---

## 四、执行流程的标准

### 4.1 反思循环标准

```python
def execute_with_reflection(self, goal: str, action_func, *args, **kwargs) -> str:
    """
    反思循环的标准流程：
    1. 执行行动
    2. 反思结果
    3. 如果不满意，优化并显示改动说明
    4. 如果错误，显示详细错误分析
    5. 记录执行历史
    """
    for iteration in range(self.max_reflections + 1):
        # 1. 执行行动
        result = action_func(*args, **kwargs) if iteration == 0 else current_result
        
        # 2. 反思
        reflection = self.reflect(goal, str(action_func), result)
        
        # 3. 如果满意，返回结果
        if reflection['is_satisfied']:
            return result
        
        # 4. 如果不满意，优化并显示改动说明
        if iteration < self.max_reflections:
            refinement = self.refine(goal, result, reflection)
            optimized_result = refinement["optimized_result"]
            changes = refinement["changes"]
            
            # 显示改动说明
            if changes:
                print(f"📝 改动说明：")
                for i, change in enumerate(changes, 1):
                    print(f"  {i}. {change}")
            
            current_result = optimized_result
```

### 4.2 错误处理流程标准

```python
try:
    # 执行操作
    result = action_func(*args, **kwargs)
except Exception as e:
    # 错误恢复：显示详细分析
    recovery = self.handle_error(e, {"goal": goal, "args": args, "kwargs": kwargs})
    
    # 显示错误分析
    print(f"\n🔍 错误分析：")
    print(f"  原因：{recovery['reason']}")
    print(f"  影响：{recovery['impact']}")
    print(f"  可能原因：{recovery['possible_causes']}")
    print(f"  恢复策略：{recovery['recovery_strategy']}")
    print(f"  预防措施：{recovery['prevention']}")
    print(f"  是否重试：{'✅ 是' if recovery['should_retry'] else '❌ 否'}\n")
    
    # 根据分析决定是否重试
    if recovery['should_retry'] and iteration < self.max_reflections:
        print("🔄 尝试恢复...")
        continue
    else:
        raise
```

---

## 五、设计原则总结

### 5.1 可见性原则

**所有操作必须可见：**
- ✅ 优化时：显示改动说明
- ✅ 错误时：显示错误分析
- ✅ 反思时：显示评估结果

### 5.2 可解释性原则

**所有操作必须可解释：**
- ✅ 改动说明：说明改了什么、为什么改
- ✅ 错误分析：说明错误原因、影响、恢复策略
- ✅ 反思评估：说明问题、改进建议

### 5.3 结构化原则

**所有输出必须结构化：**
- ✅ 使用明确的格式（正则表达式解析）
- ✅ 返回字典结构，便于程序处理
- ✅ 保留原始输出，便于调试

### 5.4 容错原则

**解析必须容错：**
- ✅ 支持多种格式（数字编号、符号列表）
- ✅ 如果格式不匹配，尝试提取关键词
- ✅ 如果解析失败，返回原始输出

---

## 六、对比：量化评估 vs 改动追踪

### 6.1 量化评估的问题

**❌ 量化评估的局限性：**
- 评分（0-100）和"满意/不满意"本质上是一样的
- 用户无法知道具体改了什么
- 评分可能不准确，缺乏可信度

### 6.2 改动追踪的优势

**✅ 改动追踪的优势：**
- 具体说明改了什么
- 解释为什么改动
- 用户可以验证改动的合理性
- 类似代码 diff，直观易懂

### 6.3 最佳实践

**推荐做法：**
- ✅ 使用改动追踪，而不是量化评分
- ✅ 显示具体的改动位置和原因
- ✅ 让用户能够验证改动的合理性

---

## 七、实现检查清单

### 反思机制检查清单

- [ ] 反思 Prompt 包含目标、行动、结果
- [ ] 反思结果包含问题分析和改进建议
- [ ] 反思结果被正确解析和存储

### 结果优化检查清单

- [ ] 优化 Prompt 要求说明改动
- [ ] 优化结果包含改动说明
- [ ] 改动说明被正确解析
- [ ] 改动说明被正确显示

### 错误处理检查清单

- [ ] 错误分析 Prompt 要求详细分析
- [ ] 错误分析包含原因、影响、策略
- [ ] 错误分析被正确解析
- [ ] 错误分析被正确显示

### 执行流程检查清单

- [ ] 优化时显示改动说明
- [ ] 错误时显示错误分析
- [ ] 执行历史被正确记录

---

## 八、参考实现

完整实现参考：`practices/practice5-reflection/agent.py`

关键方法：
- `reflect()`: 反思评估
- `refine()`: 结果优化（含改动追踪）
- `handle_error()`: 错误处理（含详细分析）
- `execute_with_reflection()`: 执行流程（含改动显示和错误分析显示）

---

## 总结

**Agent 反思与错误处理的核心标准：**

1. **可见性**：所有操作必须可见
2. **可解释性**：所有操作必须可解释
3. **结构化**：所有输出必须结构化
4. **容错性**：解析必须容错
5. **改动追踪优于量化评估**：具体说明改了什么、为什么改

遵循这些标准，可以让 Agent 的反思和错误处理过程更加透明、可信、可验证。

