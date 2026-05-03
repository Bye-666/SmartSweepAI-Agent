# 智扫通AI-Agent项目

## 📋 项目概述

**智扫通**是一个基于ReAct框架的扫地机器人智能客服系统，结合了RAG（检索增强生成）技术和LangChain/LangGraph框架，能够为用户提供专业的扫地机器人使用咨询、故障排查、维护建议以及个性化使用报告生成服务。

### 核心功能

#### 1. 智能问答服务
- 基于向量数据库的语义检索
- RAG增强的专业回答生成
- 支持多种文档格式（PDF、TXT、CSV）
- 自动文档分片和去重机制

#### 2. ReAct智能代理
- 自主思考与工具调用能力
- "思考→行动→观察→再思考"的工作流程
- 动态提示词切换机制
- 多轮对话上下文管理

#### 3. 个性化报告生成
- 用户专属使用记录查询
- 月度使用情况分析报告
- 定制化保养建议
- Markdown格式报告输出

#### 4. 环境适配咨询
- 天气信息查询
- 地理位置识别
- 环境因素对机器人使用的影响分析

---

## 🏗️ 技术架构

### 核心技术栈

1. **LangChain**: 用于构建LLM应用的核心框架
2. **LangGraph**: 提供Agent状态管理和工作流编排
3. **Chroma**: 向量数据库，存储知识库文档的向量表示
4. **Streamlit**: Web界面框架，提供用户交互界面
5. **通义千问(qwen3-max)**: 大语言模型，作为Agent的核心推理引擎
6. **DashScope(text-embedding-v4)**: 文本嵌入模型，用于向量化文档
7. **配置管理**: YAML
8. **日志系统**: Python logging（支持敏感信息脱敏）

### 设计模式

- **工厂模式**: `model/factory.py` 中使用工厂模式创建聊天模型和嵌入模型
- **单例模式**: 全局共享的模型实例、向量存储服务、配置对象
- **装饰器模式**: 使用`@tool`装饰器将普通函数转换为LangChain工具
- **中间件模式**: 通过中间件实现工具监控、日志记录、动态提示词切换

### 系统架构图

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│ React Agent  │────▶│  Middleware     │
└─────────────────┘     └──────────────┘     └─────────────────┘
                               │                       │
                               ▼                       ▼
                        ┌──────────────┐     ┌─────────────────┐
                        │ Tool System  │     │ Prompt Switcher │
                        └──────────────┘     └─────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌──────────────┐ ┌──────────┐    ┌──────────────┐
       │ RAG Service  │ │External  │    │ Weather/     │
       │              │ │Data API  │    │ Location API │
       └──────────────┘ └──────────┘    └──────────────┘
              │
              ▼
       ┌──────────────┐
       │Vector Store  │
       │ (ChromaDB)   │
       └──────────────┘
```

---

## 📁 目录结构详解

```
SmartSweepAI-Agent/
├── app.py                    # Streamlit主应用入口
├── agent/                    # Agent核心模块
│   ├── react_agent.py        # ReAct智能代理实现
│   └── tools/                # 工具和中间件
│       ├── agent_tools.py    # 7个核心工具函数
│       └── middleware.py     # 3个中间件函数
├── rag/                      # RAG检索增强生成模块
│   ├── rag_service.py        # RAG总结服务
│   └── vector_store.py       # 向量数据库服务
├── model/                    # 模型工厂
│   └── factory.py            # 聊天模型和嵌入模型工厂
├── config/                   # 配置文件目录
│   ├── agent.yml             # Agent配置
│   ├── chroma.yml            # Chroma数据库配置
│   ├── prompts.yml           # 提示词路径配置
│   └── rag.yml               # RAG模型配置
├── prompts/                  # 提示词文件
│   ├── main_prompt.txt       # 主系统提示词
│   ├── rag_summarize.txt     # RAG总结提示词
│   └── report_prompt.txt     # 报告生成提示词
├── data/                     # 数据目录
│   ├── external/             # 外部数据(CSV)
│   ├── *.pdf/txt             # 知识库文档
│   └── records.csv           # 用户使用记录
├── utils/                    # 工具类模块
│   ├── config_handler.py     # 配置加载器
│   ├── prompt_loader.py      # 提示词加载器
│   ├── file_handler.py       # 文件处理工具
│   ├── path_tools.py         # 路径工具
│   ├── logger_handler.py     # 日志处理器（支持敏感信息脱敏）
│   └── chain_debug.py        # 调试工具
└── chroma_db/                # Chroma向量数据库持久化目录
```

---

## 🔧 核心模块详解

### 1. 应用入口 (app.py)

**功能**: 使用Streamlit构建Web聊天界面

**关键流程**:
```python
用户输入 → 显示问题 → 调用Agent流式执行 → 逐字显示回答 → 保存对话历史
```

**技术亮点**:
- 使用`st.session_state`保持对话历史和Agent实例
- 实现打字机效果：通过`time.sleep(0.01)`逐字符输出
- 流式响应：使用生成器捕获并缓存完整回答

---

### 2. ReAct智能代理 (agent/react_agent.py)

**功能**: 基于ReAct框架的智能代理，实现"思考→行动→观察→再思考"的循环

**核心组件**:
- **模型**: 通义千问聊天模型
- **系统提示词**: 定义Agent行为准则和工具使用规则
- **工具列表**: 7个可用工具供Agent自主调用
- **中间件**: 3个中间件提供监控和动态能力

**执行流程**:
```python
用户问题 → 构建消息字典 → Agent.stream()流式处理 → 
遍历响应块 → 提取最新消息 → 产出内容片段
```

**关键技术**:
- `stream_mode="values"`: 返回完整状态值
- `context={"report": False}`: 初始上下文标记非报告场景
- 生成器模式支持流式输出

**工作流程**：
1. 接收用户问题
2. 分析问题并决定是否需要调用工具
3. 调用相应工具获取信息
4. 整合信息生成回答
5. 最多5次工具调用迭代

---

### 3. 工具系统 (agent/tools/agent_tools.py)

提供7个核心工具供Agent调用：

#### 3.1 rag_summarize
- **功能**: RAG检索总结，从向量库获取专业知识
- **参数**: query (检索词)
- **返回**: 基于检索资料生成的专业回答
- **应用场景**: 回答需要专业知识的问题

#### 3.2 get_weather
- **功能**: 获取城市天气信息（当前为模拟数据）
- **参数**: city (城市名)
- **返回**: 天气、温度、湿度等综合信息
- **应用场景**: 判断环境是否适合机器人使用

#### 3.3 get_user_location
- **功能**: 获取用户所在城市（当前为随机模拟）
- **参数**: 无
- **返回**: 城市名称
- **应用场景**: 配合天气工具使用

#### 3.4 get_user_id
- **功能**: 获取用户ID（当前为随机模拟）
- **参数**: 无
- **返回**: 用户ID字符串
- **应用场景**: 查询个人使用记录

#### 3.5 get_current_month
- **功能**: 获取当前月份（当前为随机模拟）
- **参数**: 无
- **返回**: YYYY-MM格式月份
- **应用场景**: 生成月度报告

#### 3.6 fetch_external_data
- **功能**: 检索用户指定月份的使用记录
- **参数**: user_id, month
- **返回**: 包含特征、效率、耗材、对比的记录
- **应用场景**: 生成个性化使用报告
- **特点**: 懒加载CSV文件到内存缓存

#### 3.7 fill_context_for_report
- **功能**: 标记报告生成场景，触发提示词切换
- **参数**: 无
- **返回**: 固定消息
- **应用场景**: 报告生成前的必要步骤
- **机制**: 通过中间件设置`context["report"]=True`

---

### 4. 中间件系统 (agent/tools/middleware.py)

提供3个中间件增强Agent能力：

#### 4.1 monitor_tool (@wrap_tool_call)
**功能**: 工具调用监控
- 记录工具名称和参数
- 记录执行结果
- 特殊处理`fill_context_for_report`工具，设置报告标志
- 异常捕获和日志记录

#### 4.2 log_before_model (@before_model)
**功能**: 模型调用前日志
- 记录即将调用LLM的时刻
- 显示消息总数
- 记录最后一条消息内容
- 用于调试和追踪Agent思考过程

#### 4.3 report_prompt_switch (@dynamic_prompt)
**功能**: 动态提示词切换
- 检查`context["report"]`标志
- 如果为True，切换到报告专用提示词
- 否则使用默认系统提示词
- 实现场景自适应的提示词管理

---

### 5. RAG服务 (rag/rag_service.py)

**功能**: 检索增强生成服务，结合向量检索和LLM生成准确回答

**核心流程**:
```python
用户提问 → 向量检索相关文档 → 格式化上下文 → 
构建提示词 → 调用LLM → 生成基于资料的回答
```

**技术实现**:
- **提示词缓存**: 类变量`_PROMPT_TEXT`避免重复读取文件
- **异常处理**: 完善的文件读取异常处理（权限、编码、空内容）
- **处理链**: `prompt_template | model | StrOutputParser()`管道式处理
- **上下文构建**: 为每个文档添加编号和内容，便于LLM理解来源

**关键方法**:
- `_load_prompt_text()`: 加载并缓存提示词
- `_init_chain()`: 初始化处理链
- `retrieve_docs()`: 向量检索相关文档
- `rag_summarize()`: 完整的RAG总结流程

**工作流程**：
1. 接收用户查询
2. 从向量库检索相关文档（top-k）
3. 格式化检索结果为上下文字符串
4. 结合用户问题和上下文调用LLM
5. 返回简洁准确的总结回答

---

### 6. 向量存储服务 (rag/vector_store.py)

**功能**: 管理Chroma向量数据库，负责文档加载、分片、向量化和检索

**初始化配置**:
- **Chroma数据库**: 集合名、嵌入函数、持久化目录
- **文本分割器**: 块大小200字符、重叠20字符、多种分隔符

**文档加载流程**:
```python
扫描数据目录 → 过滤允许的文件类型 → 计算MD5 → 
检查是否已加载 → 读取文件 → 文本分片 → 
向量化存储 → 保存MD5记录
```

**去重机制**:
- 使用MD5哈希值唯一标识文件内容
- `md5.text`文件记录已加载文件的MD5
- 避免重复加载相同内容的文件

**支持的文件格式**:
- TXT: 纯文本文档
- PDF: PDF文档（使用PyPDFLoader）
- CSV: 表格数据（使用CSVLoader）

**关键方法**:
- `get_retriever()`: 获取配置好的检索器（返回最相关的k=3个文档）
- `load_document()`: 批量加载知识库文档

**配置项 (chroma.yml)**:
```yaml
collection_name: agent           # 集合名称
persist_directory: chroma_db     # 持久化目录
k: 3                             # 检索返回数量
data_path: data                  # 数据目录
md5_hex_store: md5.text          # MD5存储文件
allow_knowledge_file_type: ["txt", "pdf", "csv"]
chunk_size: 200                  # 分片大小
chunk_overlap: 20                # 分片重叠
separators: ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
```

---

### 7. 模型工厂 (model/factory.py)

**功能**: 使用工厂模式创建和管理模型实例

**设计模式**:
- **抽象基类**: `BaseModelFactory`定义统一接口
- **具体工厂**: 
  - `ChatModelFactory`: 创建通义千问聊天模型
  - `EmbeddingsFactory`: 创建DashScope嵌入模型

**单例模式**:
- 模块级别创建全局实例`chat_model`和`embed_model`
- 所有模块共享使用，避免重复创建

**配置驱动**:
- 从`rag.yml`读取模型名称
- 易于切换不同模型

**优势**:
- 统一的模型创建接口
- 易于扩展其他模型提供商
- 集中管理模型配置

---

### 8. 配置管理 (utils/config_handler.py)

**功能**: 统一加载和管理YAML配置文件

**配置文件**:
- `rag.yml`: 聊天模型和嵌入模型名称
- `chroma.yml`: 向量数据库参数和分片设置
- `prompts.yml`: 提示词文件路径
- `agent.yml`: Agent相关配置（外部数据路径）

**优化策略**:
- 模块加载时一次性读取所有配置
- 创建全局配置对象`rag_conf`, `chroma_conf`, `prompts_conf`, `agent_conf`
- 避免运行时重复IO操作

---

### 9. 提示词管理 (utils/prompt_loader.py)

**功能**: 加载不同类型的系统提示词

**提示词类型**:
- **main_prompt.txt**: 主系统提示词，定义Agent核心行为
  - 定义ReAct代理行为准则
  - 详细说明各工具使用方法
  - 规定输出规则和思考流程
- **report_prompt.txt**: 报告生成专用提示词
  - 专注报告撰写角色
  - 限定可用工具范围
  - 规定Markdown格式输出
- **rag_summarize.txt**: RAG总结提示词（在RAG服务中直接加载）
  - 强调基于参考资料回答
  - 禁止编造信息
  - 要求简洁客观

**错误处理**:
- 配置文件路径缺失检测
- 文件不存在异常处理
- 其他读取异常捕获

---

### 10. 文件处理工具 (utils/file_handler.py)

**核心功能**:

#### 10.1 MD5计算 (`get_file_md5_hex`)
- 分片读取大文件（4KB chunks），避免内存溢出
- 二进制模式读取确保准确性
- 完善的异常处理（文件不存在、权限不足等）

#### 10.2 目录扫描 (`listdir_with_allowed_type`)
- 过滤指定扩展名的文件
- 返回完整路径元组

#### 10.3 文档加载器
- `csv_loader`: 加载CSV为LangChain文档
- `pdf_loader`: 加载PDF为LangChain文档
- `txt_loader`: 加载TXT为LangChain文档
- 统一返回Document对象列表

---

### 11. 路径工具 (utils/path_tools.py)

**功能**: 解决相对路径问题，统一路径基准

**核心方法**:
- `get_project_root()`: 基于当前文件位置推导项目根目录
- `get_abs_path(relative_path)`: 将相对路径转换为绝对路径

**优势**:
- 无论从哪里运行脚本，都能正确定位文件
- 提高代码可移植性

---

### 12. 日志系统 (utils/logger_handler.py)

**功能**: 提供配置完善的日志器，支持敏感信息脱敏

**核心特性**:
- **双输出**: 同时输出到控制台和文件
- **分级控制**: 控制台(INFO)和文件(DEBUG)不同级别
- **敏感信息脱敏**: 
  - API Key (sk-******)
  - 手机号 (1**********)
  - 邮箱 (user****@domain.com)
  - 密码/密钥 (password=******)
- **自动脱敏过滤器**: `SensitiveDataFilter`在日志记录前自动处理
- **按日期分文件**: 每天生成独立日志文件

**日志格式**:
```
2024-01-21 10:30:45 - agent - INFO - react_agent.py:25 - 日志消息
```

---

### 13. 调试工具 (utils/chain_debug.py)

**功能**: 打印LangChain提示词内容，用于调试

**特点**:
- 可选择输出到控制台或日志
- 返回原始对象，支持链式调用
- 格式化输出便于阅读

---

## 🔄 核心工作流程

### 场景1: 普通问答

```
用户: "小户型适合哪种扫地机器人？"
  ↓
app.py接收问题，调用ReactAgent.execute_stream()
  ↓
Agent分析：需要专业知识 → 决定调用rag_summarize工具
  ↓
middleware.monitor_tool记录工具调用
  ↓
rag_summarize工具 → RagSummarizeService.rag_summarize()
  ↓
向量检索相关文档（ChromaDB）
  ↓
构建上下文 + 调用LLM → 生成回答
  ↓
返回回答给用户
```

### 场景2: 天气相关咨询

```
用户: "扫地机器人在我所在地区的气温下如何保养"
  ↓
Agent分析：需要知道用户位置和天气
  ↓
第1步：调用get_user_location → 获取城市（如"深圳"）
  ↓
第2步：调用get_weather(city="深圳") → 获取天气信息
  ↓
第3步：调用rag_summarize(query="气温保养") → 获取保养知识
  ↓
整合信息 → 生成综合建议
```

### 场景3: 报告生成

```
用户: "生成我的6月使用报告"
  ↓
Agent识别为报告生成场景
  ↓
第1步：调用get_user_id → 获取用户ID（如"1001"）
  ↓
第2步：调用get_current_month → 获取月份（如"2025-06"）
  ↓
第3步：调用fill_context_for_report → 设置context["report"]=True
  ↓
middleware检测到标志 → 触发report_prompt_switch
  ↓
动态切换到报告专用提示词
  ↓
第4步：调用fetch_external_data(user_id="1001", month="2025-06")
  ↓
获取使用记录（特征、效率、耗材、对比）
  ↓
可选：调用rag_summarize获取保养建议
  ↓
使用报告提示词生成Markdown格式报告
```

---

## 💡 技术亮点

### 1. ReAct框架应用
- **Reasoning**: Agent自主思考需要什么信息
- **Acting**: 自主决定调用哪些工具
- **Observation**: 观察工具返回结果
- **Iteration**: 循环直到信息足够回答问题

### 2. RAG检索增强
- 向量相似度搜索获取相关知识
- 避免LLM幻觉，提高回答准确性
- 基于真实资料生成回答

### 3. 中间件机制
- **解耦**: 监控、日志、提示词切换与核心逻辑分离
- **灵活**: 可动态添加新中间件
- **可扩展**: 易于实现新功能

### 4. 动态提示词切换
- 根据上下文自动切换提示词
- 报告场景使用专用提示词
- 提高特定场景的表现

### 5. 流式响应
- 提升用户体验，减少等待时间
- 打字机效果更自然
- 实时反馈Agent思考过程

### 6. 完善的错误处理
- 文件读取异常处理
- 工具调用异常捕获
- 详细的日志记录

### 7. 性能优化
- 配置预加载，避免重复IO
- 提示词缓存，减少文件读取
- MD5去重，避免重复向量化
- 外部数据懒加载，按需读取

---

## 🎯 学习要点

### 对于初学者

1. **LangChain基础**:
   - 理解Tool、Agent、Chain的概念
   - 学习如何使用装饰器创建工具
   - 掌握提示词模板的使用

2. **RAG原理**:
   - 文本分片和向量化的意义
   - 向量相似度搜索的工作原理
   - 如何将检索结果融入LLM提示词

3. **设计模式**:
   - 工厂模式的实际应用
   - 单例模式的实现方式
   - 装饰器模式的妙用

### 对于进阶学习者

1. **LangGraph高级用法**:
   - 中间件的实现机制
   - 上下文传递和状态管理
   - 动态提示词切换的实现

2. **系统架构设计**:
   - 模块化设计的思想
   - 配置驱动的开发方式
   - 日志和监控系统的设计

3. **工程实践**:
   - 异常处理的完整性
   - 性能优化的策略
   - 代码注释和规范

---

## 🚀 安装与部署

### 环境要求
- Python 3.9+
- 通义千问API密钥
- DashScope API密钥

### 依赖安装

```bash
pip install streamlit langchain langgraph langchain-chroma 
pip install langchain-community dashscope pypdf
```

### 配置步骤

1. **设置API密钥**
   ```bash
   export DASHSCOPE_API_KEY="your-api-key"
   ```

2. **配置文件调整**
   - 修改 `config/rag.yml` 中的模型名称
   - 根据需要调整 `config/chroma.yml` 中的参数

3. **准备知识库数据**
   - 将文档放入 `data/` 目录
   - 支持格式: PDF, TXT, CSV

4. **初始化向量数据库**
   ```bash
   python rag/vector_store.py
   ```

5. **启动应用**
   ```bash
   streamlit run app.py
   ```

---

## 📖 使用指南

### 基本对话
直接在聊天界面输入问题，例如：
- "扫地机器人如何清理毛发缠绕？"
- "什么品牌的扫地机器人性价比高？"
- "扫地机器人显示错误代码E3是什么意思？"

### 生成使用报告
- "生成我的使用报告"
- "查看我上个月的机器人使用情况"
- "帮我分析一下本月的清洁效率"

### 环境咨询
- "今天适合让扫地机器人工作吗？"
- "潮湿天气下如何使用扫拖一体机？"
- "我家在深圳，冬天怎么保养机器人？"

---

## 👨‍💻 开发指南

### 添加新工具

1. 在 `agent/tools/agent_tools.py` 中定义工具：
```python
@tool(description="工具描述")
def new_tool(param1: str, param2: int) -> str:
    """工具实现"""
    return result
```

2. 在 `react_agent.py` 中注册工具：
```python
tools=[..., new_tool]
```

3. 在 `main_prompt.txt` 中添加使用说明

### 自定义提示词

1. 在 `prompts/` 目录创建新的提示词文件
2. 在 `config/prompts.yml` 中添加路径配置
3. 在 `utils/prompt_loader.py` 中添加加载函数
4. 在中间件或代理中使用新提示词

### 扩展向量数据库

修改 `config/chroma.yml`:
```yaml
chunk_size: 300          # 增大分片尺寸
chunk_overlap: 30        # 增加重叠
k: 5                     # 返回更多结果
```

### 更换模型

修改 `model/factory.py`:
```python
class ChatModelFactory(BaseModelFactory):
    def generator(self):
        return YourCustomModel(model="model-name")
```

---

## ⚡ 性能优化建议

1. **向量检索优化**
   - 调整chunk_size和chunk_overlap平衡精度和速度
   - 合理设置k值，避免过多无关信息
   - 定期清理和优化向量数据库

2. **缓存策略**
   - 提示词文本已实现类级别缓存
   - 可考虑添加RAG检索结果缓存
   - 外部数据可考虑Redis缓存

3. **并发处理**
   - Streamlit支持多会话
   - 注意ChromaDB的并发访问限制
   - 考虑使用连接池

4. **日志管理**
   - 定期清理旧日志文件
   - 生产环境可降低日志级别
   - 监控日志文件大小

---

## ❓ 常见问题

### Q1: 向量数据库初始化失败
**A:** 检查以下几点：
- 确认data目录存在且有文件
- 检查文件格式是否在允许列表中
- 查看logs目录下的详细错误日志
- 确认API密钥已正确设置

### Q2: 回答不准确
**A:** 可能的原因：
- 知识库中缺少相关信息
- chunk_size设置不合理
- 检索参数k值过小
- 提示词约束不够明确

### Q3: 报告生成失败
**A:** 检查：
- 用户ID是否存在于records.csv中
- 月份格式是否正确（YYYY-MM）
- fill_context_for_report是否被调用
- CSV文件格式是否正确

### Q4: 流式响应中断
**A:** 可能原因：
- 网络连接问题
- LLM API超时
- Streamlit会话状态丢失
- 检查浏览器控制台错误

---

## 🔮 未来改进方向

### 功能增强
1. **真实API集成**:
   - 接入真实天气API替换模拟数据
   - 接入用户认证系统获取真实用户信息
   - 接入物联网平台获取真实设备数据

2. **更多工具**:
   - 故障诊断工具（基于图片识别）
   - 配件推荐工具（基于使用记录）
   - 预约维修工具

3. **多轮对话优化**:
   - 增加对话记忆长度
   - 实现意图识别
   - 支持打断和澄清

4. **其他改进**:
   - 支持图片上传和识别
   - 用户反馈收集机制
   - A/B测试框架

### 性能提升
1. **向量数据库优化**:
   - 增加索引策略
   - 调整分片参数
   - 使用更高效的嵌入模型

2. **缓存机制**:
   - LLM响应缓存
   - 向量检索结果缓存
   - 工具调用结果缓存

3. **异步处理**:
   - 使用异步IO提高并发
   - 后台任务处理
   - 流式响应的优化

4. **其他优化**:
   - 负载均衡
   - 向量检索加速

### 用户体验
- 富文本渲染
- 交互式报告图表
- 语音输入输出
- 移动端适配

### 工程化改进
1. **测试覆盖**:
   - 单元测试
   - 集成测试
   - 端到端测试

2. **部署优化**:
   - Docker容器化
   - CI/CD流水线
   - 监控和告警

3. **安全性**:
   - API Key安全管理
   - 输入验证和过滤
   - 速率限制

4. **系统集成**:
   - 对接真实天气API
   - 接入实际用户数据库
   - IoT设备控制集成
   - 第三方客服平台对接

---

## 📚 学习资源

### LangChain官方文档
- https://python.langchain.com/docs/

### LangGraph文档
- https://langchain-ai.github.io/langgraph/

### Chroma文档
- https://docs.trychroma.com/

### ReAct论文
- "ReAct: Synergizing Reasoning and Acting in Language Models"

---

## 📝 总结

智扫通项目是一个优秀的LangChain应用案例，展示了：
- ✅ ReAct框架的实际应用
- ✅ RAG技术的完整实现
- ✅ 中间件系统的灵活设计
- ✅ 工程化的代码组织和注释
- ✅ 完善的错误处理和日志系统

通过深入学习这个项目，你可以掌握：
1. 如何构建基于LLM的智能Agent
2. 如何实现RAG检索增强生成
3. 如何设计可扩展的工具系统
4. 如何使用中间件增强系统能力
5. 如何进行工程化的Python项目开发

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📬 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

---

**注**: 本项目使用了以下开源库：
- LangChain
- LangGraph
- ChromaDB
- Streamlit
- DashScope SDK

感谢这些优秀项目的贡献！