# 智扫通机器人智能客服系统

## 项目概述

智扫通是一个基于LangChain和ReAct模式的扫地机器人智能客服系统，采用RAG（检索增强生成）技术，能够为用户提供专业的扫地机器人使用建议、故障排除、维护保养等咨询服务。系统支持流式响应，具备良好的用户体验和可扩展性。

## 核心功能

### 1. 智能问答服务
- 基于向量数据库的语义检索
- RAG增强的专业回答生成
- 支持多种文档格式（PDF、TXT、CSV）
- 自动文档分片和去重机制

### 2. ReAct智能代理
- 自主思考与工具调用能力
- "思考→行动→观察→再思考"的工作流程
- 动态提示词切换机制
- 多轮对话上下文管理

### 3. 个性化报告生成
- 用户专属使用记录查询
- 月度使用情况分析报告
- 定制化保养建议
- Markdown格式报告输出

### 4. 环境适配咨询
- 天气信息查询
- 地理位置识别
- 环境因素对机器人使用的影响分析

## 技术架构

### 技术栈
- **前端框架**: Streamlit
- **AI框架**: LangChain, LangGraph
- **向量数据库**: ChromaDB
- **大语言模型**: 通义千问 (Qwen)
- **嵌入模型**: DashScope Embeddings
- **配置管理**: YAML
- **日志系统**: Python logging

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

## 项目结构

```
zst_agent/
├── agent/                      # 智能代理模块
│   ├── react_agent.py         # ReAct代理主类
│   └── tools/                 # 工具和中间件
│       ├── agent_tools.py     # 工具定义
│       └── middleware.py      # 中间件逻辑
├── config/                     # 配置文件目录
│   ├── agent.yml              # 代理配置
│   ├── chroma.yml             # 向量数据库配置
│   ├── prompts.yml            # 提示词路径配置
│   └── rag.yml                # RAG模型配置
├── data/                       # 数据目录
│   ├── external/              # 外部数据
│   │   └── records.csv        # 用户使用记录
│   ├── 扫地机器人100问.pdf
│   ├── 扫地机器人100问2.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   └── 选购指南.txt
├── model/                      # 模型工厂
│   └── factory.py             # 模型创建工厂
├── prompts/                    # 提示词模板
│   ├── main_prompt.txt        # 主系统提示词
│   ├── rag_summarize.txt      # RAG总结提示词
│   └── report_prompt.txt      # 报告生成提示词
├── rag/                        # RAG服务模块
│   ├── rag_service.py         # RAG总结服务
│   └── vector_store.py        # 向量存储服务
├── utils/                      # 工具函数
│   ├── chain_debug.py         # 链调试工具
│   ├── config_handler.py      # 配置处理器
│   ├── file_handler.py        # 文件处理器
│   ├── logger_handler.py      # 日志处理器
│   ├── path_tools.py          # 路径工具
│   └── prompt_loader.py       # 提示词加载器
├── app.py                      # 应用入口
├── .gitignore
└── README.md
```

## 核心模块详解

### 1. ReAct代理 (agent/react_agent.py)

ReAct代理是系统的核心，实现了Reasoning + Acting模式：

**主要特性：**
- 使用LangChain的`create_agent`创建
- 集成7个专用工具
- 3个中间件：工具监控、模型调用前日志、动态提示词切换
- 支持流式响应输出

**工作流程：**
1. 接收用户问题
2. 分析问题并决定是否需要调用工具
3. 调用相应工具获取信息
4. 整合信息生成回答
5. 最多5次工具调用迭代

### 2. 工具系统 (agent/tools/agent_tools.py)

系统提供7个核心工具：

#### rag_summarize
- **功能**: 从向量库检索扫地机器人相关知识
- **输入**: query (检索词)
- **输出**: 专业知识字符串
- **应用场景**: 获取产品使用、故障处理、维护保养等专业信息

#### get_weather
- **功能**: 获取指定城市天气信息
- **输入**: city (城市名)
- **输出**: 天气详情字符串
- **应用场景**: 判断环境是否适合机器人使用

#### get_user_location
- **功能**: 获取用户所在城市
- **输入**: 无
- **输出**: 城市名称
- **应用场景**: 配合天气工具使用

#### get_user_id
- **功能**: 获取用户唯一标识
- **输入**: 无
- **输出**: 用户ID字符串
- **应用场景**: 生成个性化报告

#### get_current_month
- **功能**: 获取当前月份
- **输入**: 无
- **输出**: YYYY-MM格式月份
- **应用场景**: 查询指定月份的使用记录

#### fetch_external_data
- **功能**: 检索用户指定月份的使用记录
- **输入**: user_id, month
- **输出**: 结构化使用记录
- **应用场景**: 生成个人使用报告

#### fill_context_for_report
- **功能**: 为报告生成场景注入上下文
- **输入**: 无
- **输出**: 无返回值
- **应用场景**: 报告生成的前置工具，触发提示词切换

### 3. 中间件系统 (agent/tools/middleware.py)

三个关键中间件：

#### monitor_tool
- 包装所有工具调用
- 记录工具执行日志
- 检测`fill_context_for_report`调用，设置报告上下文标志

#### log_before_model
- 在每次调用LLM前记录日志
- 显示消息数量和最后一条消息内容
- 便于调试和问题追踪

#### report_prompt_switch
- 动态提示词切换
- 根据上下文中的`report`标志选择提示词
- 普通对话使用`main_prompt.txt`
- 报告生成使用`report_prompt.txt`

### 4. RAG服务 (rag/)

#### VectorStoreService (vector_store.py)
**核心功能：**
- 基于ChromaDB的向量存储
- 支持PDF、TXT、CSV三种文件格式
- MD5哈希去重机制
- 递归字符文本分片
- 可配置的检索参数

**初始化流程：**
1. 扫描data目录下允许的文件类型
2. 计算文件MD5值
3. 检查是否已存在于知识库
4. 加载文档并进行文本分片
5. 生成向量并存储到ChromaDB
6. 保存MD5值用于后续去重

**配置项 (chroma.yml):**
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

#### RagSummarizeService (rag_service.py)
**核心功能：**
- 基于检索结果生成总结回答
- 提示词缓存机制
- LangChain链式调用
- 严格的回答约束（仅基于参考资料）

**工作流程：**
1. 接收用户查询
2. 从向量库检索相关文档（top-k）
3. 格式化检索结果为上下文字符串
4. 结合用户问题和上下文调用LLM
5. 返回简洁准确的总结回答

### 5. 模型工厂 (model/factory.py)

采用工厂模式创建模型实例：

**ChatModelFactory:**
- 创建聊天模型实例
- 使用通义千问 (qwen3-max)

**EmbeddingsFactory:**
- 创建嵌入模型实例
- 使用DashScope embeddings (text-embedding-v4)

**优势：**
- 统一的模型创建接口
- 易于扩展其他模型提供商
- 集中管理模型配置

### 6. 配置管理 (utils/config_handler.py)

基于YAML的配置管理系统：

**配置文件：**
- `rag.yml`: RAG相关配置（模型名称）
- `chroma.yml`: 向量数据库配置
- `prompts.yml`: 提示词文件路径
- `agent.yml`: 代理配置（外部数据路径）

**特点：**
- 启动时一次性加载所有配置
- 全局配置对象可直接导入使用
- 支持UTF-8编码

### 7. 提示词管理 (utils/prompt_loader.py)

**提示词类型：**
1. **main_prompt.txt**: 主系统提示词
   - 定义ReAct代理行为准则
   - 详细说明各工具使用方法
   - 规定输出规则和思考流程

2. **report_prompt.txt**: 报告生成提示词
   - 专注报告撰写角色
   - 限定可用工具范围
   - 规定Markdown格式输出

3. **rag_summarize.txt**: RAG总结提示词
   - 强调基于参考资料回答
   - 禁止编造信息
   - 要求简洁客观

**加载机制：**
- 通过配置文件管理路径
- 运行时动态加载
- 完善的异常处理

### 8. 文件处理 (utils/file_handler.py)

**核心功能：**

#### MD5计算
- 分片读取大文件（4KB）
- 防止内存溢出
- 完善的错误处理

#### 文件列表
- 按扩展名过滤
- 返回目录下所有符合条件的文件

#### 文档加载器
- `csv_loader`: CSV文件加载
- `pdf_loader`: PDF文件加载
- `txt_loader`: TXT文件加载
- 统一返回Document对象列表

### 9. 日志系统 (utils/logger_handler.py)

**特性：**
- 双输出：控制台 + 文件
- 敏感信息自动脱敏
- 按日期分割日志文件
- 详细的日志格式（时间、模块、行号）

**脱敏规则：**
- API密钥 (sk-*)
- 手机号
- 邮箱地址
- 密码/密钥字段

**日志级别：**
- 控制台: INFO
- 文件: DEBUG

### 10. 路径工具 (utils/path_tools.py)

**解决的问题：**
- 跨平台路径兼容性
- 相对路径转绝对路径
- 无论从哪里运行都能正确定位资源

**核心函数：**
- `get_project_root()`: 获取项目根目录
- `get_abs_path(relative_path)`: 转换为绝对路径

## 数据流示例

### 场景1: 普通问答

```
用户: "小户型适合哪种扫地机器人？"
  ↓
Streamlit UI接收输入
  ↓
ReactAgent.execute_stream()
  ↓
LLM分析问题 → 需要专业知识
  ↓
调用 rag_summarize("小户型 扫地机器人")
  ↓
VectorStoreService检索相似文档
  ↓
RagSummarizeService生成总结
  ↓
LLM整合信息生成回答
  ↓
流式返回给用户
```

### 场景2: 报告生成

```
用户: "生成我6月份的使用报告"
  ↓
ReactAgent识别报告意图
  ↓
调用 get_user_id() → 获取用户ID
  ↓
调用 get_current_month() → 获取月份
  ↓
调用 fill_context_for_report()
  ↓
Middleware检测到调用 → 设置 context["report"]=True
  ↓
Dynamic Prompt切换为 report_prompt.txt
  ↓
调用 fetch_external_data(user_id, month)
  ↓
从CSV文件检索使用记录
  ↓
LLM基于报告提示词生成Markdown报告
  ↓
返回格式化报告
```

### 场景3: 环境适配咨询

```
用户: "扫地机器人在我所在地区的气温下如何保养"
  ↓
ReactAgent分析问题
  ↓
调用 get_user_location() → 获取城市
  ↓
调用 get_weather(city) → 获取天气
  ↓
调用 rag_summarize("气温 保养") → 获取保养知识
  ↓
LLM整合天气信息和保养建议
  ↓
生成个性化保养建议
```

## 安装与部署

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

## 使用指南

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

## 开发指南

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

## 性能优化建议

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

## 常见问题

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

## 未来改进方向

1. **功能增强**
   - 支持图片上传和识别
   - 多轮对话记忆优化
   - 用户反馈收集机制
   - A/B测试框架

2. **性能提升**
   - 异步工具调用
   - 向量检索加速
   - 响应缓存策略
   - 负载均衡

3. **用户体验**
   - 富文本渲染
   - 交互式报告图表
   - 语音输入输出
   - 移动端适配

4. **系统集成**
   - 对接真实天气API
   - 接入实际用户数据库
   - IoT设备控制集成
   - 第三方客服平台对接

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

---

**注**: 本项目使用了以下开源库：
- LangChain
- LangGraph
- ChromaDB
- Streamlit
- DashScope SDK

感谢这些优秀项目的贡献！