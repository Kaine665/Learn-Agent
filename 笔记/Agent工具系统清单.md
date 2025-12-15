# Agent 工具系统清单

## 工具分类原则

### 核心工具（Core Tools）
**每个 Agent 都必须具备，否则无法正常工作**

- ✅ **finish**：任务完成标记
- ✅ **answer/write**：输出内容给用户
- ✅ **think/reason**：显式思考（可选，但推荐）

### 通用工具（Common Tools）
**大多数 Agent 都会用到，但不是必须的**

- 🔧 **search**：信息搜索
- 🔧 **calculate**：数学计算
- 🔧 **file_operations**：文件操作

### 专业工具（Specialized Tools）
**特定领域的 Agent 才需要**

- 📊 **data_analysis**：数据分析
- 🎨 **image_generation**：图像生成
- 💻 **code_execution**：代码执行
- 🌐 **web_scraping**：网页抓取

---

## 工具清单（按调用频率排序）

### 1. finish（核心工具）

**调用频率：** ⭐⭐⭐⭐⭐（每个任务结束时必调用）

**功能：** 标记任务完成，结束 Agent 循环

**实现方式：**
- ✅ **自己实现**：最简单的工具，只需返回状态标记
- 实现代码：`return "任务完成"`

**最佳效果：**
- ✅ 100% 可靠
- ✅ 零延迟
- ✅ 无成本

**设计要点：**
- 必须显式调用，不能隐式完成
- 可以携带最终总结信息

---

### 2. answer / write（核心工具）

**调用频率：** ⭐⭐⭐⭐⭐（几乎每个任务都需要）

**功能：** 输出内容给用户，用于逐步完成任务

**实现方式：**
- ✅ **自己实现**：最简单的工具，直接返回内容
- 实现代码：`return f"回答：{content}"` 或 `return f"已输出：{content[:100]}..."`

**最佳效果：**
- ✅ 支持逐步输出
- ✅ 可以控制输出长度
- ✅ 可以格式化输出

**设计要点：**
- 这是 ReAct Agent 能够逐步完成任务的关键
- 可以添加参数：`content`, `format`（markdown/plain）, `summary`（是否只输出摘要）

**变体：**
- `answer`：直接回答用户
- `write`：写入内容（可以用于文件、输出等）
- `output`：通用输出

---

### 3. search（通用工具）

**调用频率：** ⭐⭐⭐⭐（信息查询类任务高频使用）

**功能：** 搜索信息（网页、知识库、文档等）

**实现方式：**
1. **OpenAI 自己实现**：使用 Bing Search API（需要 API Key）
   - 优点：官方支持，质量高
   - 缺点：需要额外 API Key，有成本

2. **开源项目**：
   - **DuckDuckGo Search**：`duckduckgo-search` 库
     ```python
     from duckduckgo_search import DDGS
     def search(query: str) -> str:
         with DDGS() as ddgs:
             results = list(ddgs.text(query, max_results=5))
             return format_results(results)
     ```
   - **Google Search API**：`googlesearch-python` 库
   - **SerpAPI**：商业 API，质量高但收费

3. **自己实现**：
   - 使用 `requests` + `BeautifulSoup` 抓取
   - 使用向量数据库（如 ChromaDB）进行语义搜索

**最佳效果：**
- ✅ 返回相关、准确的结果
- ✅ 支持多种搜索源（网页、学术、图片等）
- ✅ 可以过滤和排序结果
- ✅ 支持实时搜索

**设计要点：**
- 参数：`query`, `num_results`, `search_type`（web/academic/image）
- 返回格式化的搜索结果摘要

---

### 4. calculate（通用工具）

**调用频率：** ⭐⭐⭐（数学计算类任务）

**功能：** 执行数学计算

**实现方式：**
1. **自己实现**：使用 Python `eval`（需安全限制）
   ```python
   def calculate(expression: str) -> str:
       allowed_chars = set('0123456789+-*/()., ')
       if all(c in allowed_chars for c in expression):
           return str(eval(expression, {"__builtins__": {}}, {}))
   ```

2. **开源项目**：
   - **SymPy**：符号数学计算
     ```python
     from sympy import sympify
     def calculate(expression: str) -> str:
         return str(sympify(expression).evalf())
     ```
   - **NumPy**：数值计算
   - **Wolfram Alpha API**：高级数学计算（商业）

**最佳效果：**
- ✅ 支持基本数学运算
- ✅ 支持符号计算（如求导、积分）
- ✅ 支持科学计算（三角函数、对数等）
- ✅ 错误处理完善

**设计要点：**
- 必须限制可执行的代码，防止安全漏洞
- 支持多种数学表达式格式

---

### 5. file_read（通用工具）

**调用频率：** ⭐⭐⭐（文件操作类任务）

**功能：** 读取文件内容

**实现方式：**
- ✅ **自己实现**：Python 标准库 `open()`
  ```python
  def file_read(filepath: str) -> str:
      with open(filepath, 'r', encoding='utf-8') as f:
          return f.read()
  ```

**最佳效果：**
- ✅ 支持多种文件格式（txt, json, csv, md 等）
- ✅ 支持大文件分块读取
- ✅ 错误处理（文件不存在、权限等）

**设计要点：**
- 参数：`filepath`, `encoding`, `max_size`（限制读取大小）
- 安全限制：只能读取指定目录的文件

---

### 6. file_write（通用工具）

**调用频率：** ⭐⭐⭐（文件操作类任务）

**功能：** 写入文件内容

**实现方式：**
- ✅ **自己实现**：Python 标准库 `open()`
  ```python
  def file_write(filepath: str, content: str) -> str:
      with open(filepath, 'w', encoding='utf-8') as f:
          f.write(content)
      return f"已写入文件：{filepath}"
  ```

**最佳效果：**
- ✅ 支持多种文件格式
- ✅ 支持追加模式
- ✅ 自动创建目录

**设计要点：**
- 参数：`filepath`, `content`, `mode`（w/a）
- 安全限制：只能写入指定目录

---

### 7. code_execute（专业工具）

**调用频率：** ⭐⭐（代码执行类任务）

**功能：** 执行代码并返回结果

**实现方式：**
1. **开源项目**：
   - **Jupyter Kernel**：使用 `jupyter_client` 执行代码
   - **Docker**：在隔离容器中执行代码
   - **CodeT5 / CodeBERT**：代码理解工具

2. **自己实现**：
   - 使用 `subprocess` 执行（不安全）
   - 使用沙箱环境（如 `pypy-sandbox`）

**最佳效果：**
- ✅ 支持多种编程语言（Python, JavaScript, etc.）
- ✅ 安全隔离执行
- ✅ 返回执行结果和错误信息
- ✅ 支持交互式执行

**设计要点：**
- 必须在隔离环境中执行
- 限制执行时间和资源
- 参数：`code`, `language`, `timeout`

---

### 8. web_scrape（专业工具）

**调用频率：** ⭐⭐（网页抓取类任务）

**功能：** 抓取网页内容

**实现方式：**
1. **开源项目**：
   - **BeautifulSoup**：HTML 解析
     ```python
     from bs4 import BeautifulSoup
     import requests
     def web_scrape(url: str) -> str:
         response = requests.get(url)
         soup = BeautifulSoup(response.content, 'html.parser')
         return soup.get_text()
     ```
   - **Scrapy**：专业爬虫框架
   - **Playwright / Selenium**：浏览器自动化（处理 JS）

**最佳效果：**
- ✅ 支持动态网页（JavaScript）
- ✅ 自动处理反爬虫机制
- ✅ 提取结构化数据
- ✅ 支持多种内容类型（文本、图片、链接）

**设计要点：**
- 参数：`url`, `selector`（CSS/XPath）, `wait_time`（等待 JS 加载）
- 遵守 robots.txt
- 限制请求频率

---

### 9. image_generate（专业工具）

**调用频率：** ⭐⭐（图像生成类任务）

**功能：** 生成图像

**实现方式：**
1. **OpenAI 自己实现**：DALL-E API
   - 优点：质量高，官方支持
   - 缺点：需要 API Key，有成本

2. **开源项目**：
   - **Stable Diffusion**：`diffusers` 库
     ```python
     from diffusers import StableDiffusionPipeline
     def image_generate(prompt: str) -> str:
         pipe = StableDiffusionPipeline.from_pretrained(...)
         image = pipe(prompt).images[0]
         return save_image(image)
     ```
   - **Midjourney API**：商业 API
   - **DALL-E Mini**：开源替代品

**最佳效果：**
- ✅ 高质量图像生成
- ✅ 支持多种风格
- ✅ 快速生成（几秒内）
- ✅ 支持图像编辑和变体

**设计要点：**
- 参数：`prompt`, `style`, `size`, `num_images`
- 返回图像 URL 或 base64

---

### 10. data_analysis（专业工具）

**调用频率：** ⭐⭐（数据分析类任务）

**功能：** 分析数据（统计、可视化、机器学习等）

**实现方式：**
1. **开源项目**：
   - **Pandas**：数据处理
     ```python
     import pandas as pd
     def data_analysis(filepath: str, analysis_type: str) -> str:
         df = pd.read_csv(filepath)
         if analysis_type == "summary":
             return df.describe().to_string()
     ```
   - **NumPy**：数值计算
   - **Matplotlib / Plotly**：数据可视化
   - **Scikit-learn**：机器学习

**最佳效果：**
- ✅ 支持多种数据格式（CSV, JSON, Excel 等）
- ✅ 自动数据清洗
- ✅ 生成统计报告
- ✅ 支持可视化图表

**设计要点：**
- 参数：`data_source`, `analysis_type`, `output_format`
- 返回分析结果和可视化图表

---

### 11. database_query（专业工具）

**调用频率：** ⭐（数据库操作类任务）

**功能：** 查询数据库

**实现方式：**
1. **开源项目**：
   - **SQLAlchemy**：ORM 框架
   - **pymongo**：MongoDB 客户端
   - **psycopg2**：PostgreSQL 客户端

**最佳效果：**
- ✅ 支持多种数据库（SQL, NoSQL）
- ✅ 安全查询（防止 SQL 注入）
- ✅ 返回结构化数据
- ✅ 支持复杂查询

**设计要点：**
- 参数：`query`, `database_type`, `connection_string`
- 必须使用参数化查询
- 限制查询复杂度

---

### 12. api_call（专业工具）

**调用频率：** ⭐（API 调用类任务）

**功能：** 调用外部 API

**实现方式：**
- ✅ **自己实现**：使用 `requests` 库
  ```python
  import requests
  def api_call(url: str, method: str, params: dict) -> str:
      response = requests.request(method, url, params=params)
      return response.json()
  ```

**最佳效果：**
- ✅ 支持 RESTful API
- ✅ 支持 GraphQL
- ✅ 错误处理和重试
- ✅ 支持认证（API Key, OAuth）

**设计要点：**
- 参数：`url`, `method`, `headers`, `body`
- 限制可调用的 API（白名单）
- 超时和重试机制

---

## 工具实现优先级

### 第一阶段（必须实现）
1. ✅ **finish**：任务完成标记
2. ✅ **answer/write**：输出内容
3. ✅ **think**：显式思考（可选但推荐）

### 第二阶段（通用工具）
4. 🔧 **search**：信息搜索（使用 DuckDuckGo 或 OpenAI Bing）
5. 🔧 **calculate**：数学计算（使用 SymPy）
6. 🔧 **file_read/write**：文件操作（Python 标准库）

### 第三阶段（专业工具）
7. 📊 **code_execute**：代码执行（使用 Docker 沙箱）
8. 📊 **web_scrape**：网页抓取（使用 BeautifulSoup/Playwright）
9. 📊 **image_generate**：图像生成（使用 DALL-E 或 Stable Diffusion）
10. 📊 **data_analysis**：数据分析（使用 Pandas）

---

## 工具设计最佳实践

### 1. 统一接口
```python
def tool_name(param1: str, param2: int) -> str:
    """
    工具描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        返回结果说明
    """
    # 实现
    return result
```

### 2. 错误处理
```python
try:
    result = execute_tool()
    return f"成功：{result}"
except Exception as e:
    return f"错误：{str(e)}"
```

### 3. 安全限制
- 文件操作：限制目录范围
- 代码执行：沙箱隔离
- API 调用：白名单机制
- 计算：限制可执行代码

### 4. 返回格式
- 成功：返回结果或状态
- 失败：返回错误信息
- 进度：返回进度百分比

---

## 总结

### 核心工具（必须）
- **finish**：任务完成标记
- **answer/write**：输出内容
- **think**：显式思考

### 通用工具（推荐）
- **search**：信息搜索
- **calculate**：数学计算
- **file_operations**：文件操作

### 专业工具（按需）
- **code_execute**：代码执行
- **web_scrape**：网页抓取
- **image_generate**：图像生成
- **data_analysis**：数据分析
- **database_query**：数据库查询
- **api_call**：API 调用

**关键洞察：**
- ✅ **finish 作为 action 很精妙**：显式控制任务结束
- ✅ **answer/write 是核心**：没有它就无法逐步完成任务
- ✅ **工具选择要平衡**：核心工具必须，通用工具推荐，专业工具按需
