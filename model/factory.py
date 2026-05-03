# 导入必要的抽象基类和LangChain模型相关模块
from abc import ABC  # 抽象基类，用于定义接口规范
from abc import abstractmethod  # 抽象方法装饰器
from langchain_community.chat_models.tongyi import ChatTongyi, BaseChatModel  # 通义千问聊天模型
from langchain_community.embeddings import DashScopeEmbeddings  # 阿里云DashScope嵌入模型
from langchain_core.embeddings import Embeddings  # LangChain嵌入模型基类
from typing import Optional  # 可选类型提示
from utils.config_handler import rag_conf  # RAG配置文件，包含模型名称等信息


class BaseModelFactory(ABC):
    """
    模型工厂抽象基类，定义模型创建的统一接口。
    使用工厂模式封装不同类型的模型创建逻辑，提高代码可维护性和扩展性。
    """
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        抽象方法：生成模型实例。
        子类必须实现此方法来创建具体的模型对象。
        
        Returns:
            Optional[Embeddings | BaseChatModel]: 返回嵌入模型或聊天模型实例，可能为None
        """
        pass


class ChatModelFactory(BaseModelFactory):
    """
    聊天模型工厂类，负责创建和配置大语言聊天模型。
    当前使用阿里云通义千问模型作为聊天引擎。
    """
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        创建聊天模型实例。
        
        Returns:
            ChatTongyi: 通义千问聊天模型实例，使用配置中指定的模型名称
        """
        # 从配置中读取聊天模型名称并创建实例
        return ChatTongyi(model=rag_conf["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    """
    嵌入模型工厂类，负责创建和配置文本嵌入模型。
    嵌入模型用于将文本转换为向量表示，支持语义相似度计算。
    """
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        创建嵌入模型实例。
        
        Returns:
            DashScopeEmbeddings: 阿里云DashScope嵌入模型实例，使用配置中指定的模型名称
        """
        # 从配置中读取嵌入模型名称并创建实例
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


# 创建全局聊天模型实例（单例模式）
# 应用启动时初始化一次，所有模块共享使用
chat_model = ChatModelFactory().generator()
# 创建全局嵌入模型实例（单例模式）
# 用于向量数据库的文本向量化操作
embed_model = EmbeddingsFactory().generator()
