# 导入必要的LangChain核心模块和自定义服务
from langchain_core.documents import Document  # LangChain文档对象，用于表示文本块及其元数据
from langchain_core.prompts import PromptTemplate  # 提示词模板类，用于构建动态提示词
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser  # 输出解析器，StrOutputParser用于将模型输出转换为字符串
from rag.vector_store import VectorStoreService  # 向量存储服务类，负责向量数据库操作
from utils.logger_handler import logger  # 日志处理器，用于记录运行日志
from utils.config_handler import prompts_conf  # 提示词配置，从YAML文件加载的配置信息
from langchain_core.runnables import RunnableLambda  # LangChain可运行组件，用于构建处理链
from utils.chain_debug import print_prompt  # 调试工具，用于打印提示词内容
from model.factory import chat_model  # 聊天模型工厂，提供大语言模型实例
from utils.path_tools import get_abs_path  # 路径工具，用于获取绝对路径


class RagSummarizeService:
    """
    RAG（检索增强生成）总结服务类。
    结合向量检索和大语言模型，基于检索到的相关资料生成准确的回答。
    RAG流程：用户提问 → 向量检索相关文档 → 将文档作为上下文输入给LLM → LLM生成基于上下文的回答
    """
    # 类变量缓存，所有实例共用，避免重复读取提示词文件
    _PROMPT_TEXT: str = None

    def __init__(self, vector_store: VectorStoreService):
        """
        初始化RAG总结服务。
        
        Args:
            vector_store (VectorStoreService): 向量存储服务实例，用于文档检索
        """
        self.vector_store = vector_store  # 保存向量存储服务引用
        self.retriever = self.vector_store.get_retriever()  # 获取文档检索器，用于根据查询检索相关文档
        self.prompt_text = self._load_prompt_text()  # 加载RAG总结用的提示词文本
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)  # 从文本创建提示词模板对象
        self.model = chat_model  # 获取聊天模型实例
        self.chain = self._init_chain()  # 初始化处理链（提示词模板 → 模型 → 输出解析器）

    def _load_prompt_text(self) -> str:
        """
        加载RAG总结提示词文本，使用类级别缓存避免重复文件读取。
        
        Returns:
            str: 提示词文本内容
            
        Raises:
            PermissionError: 当无权限读取提示词文件时
            ValueError: 当提示词文件编码错误或内容为空时
            RuntimeError: 当读取文件发生其他异常时
        """
        if self._PROMPT_TEXT is not None:
            # 如果已缓存提示词文本，直接返回缓存值，避免重复文件IO操作
            return self._PROMPT_TEXT

        # 从配置中获取提示词文件路径并转换为绝对路径
        path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
        try:
            # 以UTF-8编码读取提示词文件
            with open(path, "r", encoding="utf-8") as f:
                prompt_text = f.read().strip()  # 读取全部内容并去除首尾空白
        except PermissionError:
            # 处理文件权限错误
            logger.error(f"无权限读取提示词文件：{path}")
            raise PermissionError(f"无权限读取提示词文件：{path}")
        except UnicodeDecodeError:
            # 处理文件编码错误，要求必须是UTF-8编码
            logger.error(f"提示词文件编码错误（需UTF-8）：{path}")
            raise ValueError(f"提示词文件编码错误（需UTF-8）：{path}")
        except Exception as e:
            # 处理其他可能的异常（如文件不存在等）
            logger.error(f"读取提示词文件失败：{str(e)}")
            raise RuntimeError(f"读取提示词文件失败：{str(e)}")

        # 验证提示词内容不为空
        if not prompt_text:
            logger.error(f"提示词文件内容为空：{path}")
            raise ValueError(f"提示词文件内容为空：{path}")

        # 将读取的提示词文本缓存到类变量，供后续实例复用
        self._PROMPT_TEXT = prompt_text
        return prompt_text

    def _init_chain(self):
        """
        初始化RAG处理链，使用LangChain的管道语法构建处理流程。
        处理链顺序：提示词模板 → 聊天模型 → 字符串输出解析器
        
        Returns:
            Runnable: 可运行的处理链对象
        """
        # 使用管道操作符|串联各个组件，形成完整的处理链
        # 1. prompt_template: 接收input和context参数，格式化生成完整提示词
        # 2. self.model: 调用大语言模型生成回答
        # 3. StrOutputParser(): 将模型输出解析为纯字符串
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retrieve_docs(self, query: str) -> list[Document]:
        """
        根据查询语句从向量数据库中检索相关文档。
        
        Args:
            query (str): 用户查询语句
            
        Returns:
            list[Document]: 检索到的相关文档列表，按相关性排序
        """
        return self.retriever.invoke(query)  # 调用检索器的invoke方法执行向量相似度搜索

    def rag_summarize(self, query: str) -> str:
        """
        执行完整的RAG总结流程：检索相关文档 → 构建上下文 → 调用LLM生成回答。
        
        Args:
            query (str): 用户查询问题
            
        Returns:
            str: 基于检索资料生成的总结回答
        """
        # 构建输入字典，包含两个关键参数：
        # - input: 用户的原始查询
        # - context: 从向量库检索到的参考资料
        input_dict = {}

        # 第一步：从向量数据库中检索与查询相关的文档
        context_docs = self.retrieve_docs(query)
        
        # 第二步：将检索到的文档格式化为上下文字符串
        context = ""
        counter = 0
        for doc in context_docs:  # 遍历每个检索到的文档
            counter += 1
            # 为每个文档添加编号、内容和元数据信息，便于LLM理解来源
            context += f"【参考资料{counter}】：参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        
        # 第三步：设置输入参数字典
        input_dict["input"] = query  # 用户原始问题
        input_dict["context"] = context  # 格式化后的参考资料上下文

        # 第四步：调用处理链生成最终回答
        # 处理链会自动完成：提示词格式化 → 调用LLM → 解析输出
        return self.chain.invoke(input_dict)


# for testing
if __name__ == '__main__':
    vs = VectorStoreService()
    rag = RagSummarizeService(vs)

    print(rag.rag_summarize("小户型适合哪种扫地机器人？"))
