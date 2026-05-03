# 导入必要的LangChain和自定义模块
from langchain_core.documents import Document  # LangChain文档对象，表示文本块及其元数据
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 递归字符文本分割器，用于将长文本切分为小块
from model.factory import embed_model  # 嵌入模型工厂，提供文本向量化能力
from langchain_chroma import Chroma  # Chroma向量数据库封装类
from utils.config_handler import chroma_conf  # Chroma配置文件，包含数据库参数
import os  # 操作系统模块，用于文件路径操作
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, csv_loader, pdf_loader, txt_loader  # 文件处理工具
from utils.logger_handler import logger  # 日志处理器
from utils.path_tools import get_abs_path  # 路径工具，用于获取绝对路径


class VectorStoreService:
    """
    向量存储服务类，负责管理Chroma向量数据库的操作。
    主要功能包括：文档加载、文本分片、向量嵌入、存储和检索。
    使用MD5哈希值避免重复加载相同内容的文件，提高效率。
    """
    def __init__(self):
        """
        初始化向量存储服务，配置Chroma数据库和文本分割器。
        """
        # 初始化Chroma向量数据库实例
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],  # 集合名称，用于隔离不同项目的向量数据
            embedding_function=embed_model,  # 嵌入函数，用于将文本转换为向量
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),  # 持久化目录，保存向量数据库到磁盘
        )

        # 初始化递归字符文本分割器，用于将长文档切分为合适大小的片段
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],  # 每个文本块的大小（字符数）
            chunk_overlap=chroma_conf["chunk_overlap"],  # 文本块之间的重叠字符数，保持上下文连贯性
            separators=chroma_conf["separators"],  # 分隔符列表，按优先级尝试不同的分割点
            length_function=len,  # 长度计算函数，使用内置len函数计算字符数
        )

    def get_retriever(self):
        """
        获取文档检索器，用于根据查询语句检索相关文档。
        
        Returns:
            VectorStoreRetriever: 配置好的检索器对象，使用相似度搜索返回最相关的k个文档
        """
        # 将向量存储转换为检索器，并设置检索参数
        # search_kwargs={"k": chroma_conf["k"]} 表示每次检索返回最相关的前k个文档
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """
        加载知识库文档到向量数据库中。
        该函数会扫描配置的数据目录，读取支持的文件类型（txt、pdf、csv），
        进行文本分片和向量化后存入Chroma数据库。使用MD5哈希值避免重复加载。
        """

        def check_md5_hex(md5_for_check):
            """
            检查文件的MD5哈希值是否已存在于记录中，用于判断文件是否已加载。
            
            Args:
                md5_for_check (str): 待检查的文件MD5哈希值
                
            Returns:
                bool: 如果MD5已存在返回True，否则返回False
            """
            # 如果MD5记录文件不存在，创建一个空文件
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False

            # 读取MD5记录文件，逐行比对
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True  # 找到匹配的MD5，说明文件已加载过

            return False  # 未找到匹配，文件未加载过

        def save_md5_hex(md5_for_save):
            """
            将文件的MD5哈希值保存到记录文件中，标记该文件已加载。
            
            Args:
                md5_for_save (str): 要保存的文件MD5哈希值
            """
            # 以追加模式打开MD5记录文件，写入新的MD5值
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save+"\n")

        def get_file_documents(read_path: str):
            """
            根据文件扩展名选择合适的加载器读取文档。
            
            Args:
                read_path (str): 文件路径
                
            Returns:
                list[Document]: 读取到的文档列表，如果文件格式不支持则返回空列表
            """
            # 根据文件扩展名选择对应的加载器
            if read_path.endswith("txt"):
                return txt_loader(read_path)  # 使用文本加载器
            elif read_path.endswith("pdf"):
                return pdf_loader(read_path)  # 使用PDF加载器
            elif read_path.endswith("csv"):
                return csv_loader(read_path)  # 使用CSV加载器
            else:
                return []  # 不支持的文件格式，返回空列表

        # 获取数据目录下所有允许类型的文件列表
        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),  # 数据目录的绝对路径
            tuple(chroma_conf["allow_knowledge_file_type"])  # 允许的文件类型元组，如("txt", "pdf", "csv")
        )

        # 遍历每个允许的文件，进行加载处理
        for path in allowed_files_path:
            # 计算文件的MD5哈希值，用于去重判断
            md5_hex = get_file_md5_hex(path)

            # 如果MD5计算失败，跳过该文件
            if not md5_hex:  # 处理MD5计算失败的情况
                logger.warning(f"[加载知识库] {path} MD5计算失败，跳过")
                continue

            # 检查该文件是否已经加载过（通过MD5比对）
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库] {path} 内容已经存在于知识库，跳过")
                continue

            try:
                # 第一步：读取文件内容为文档列表
                documents: list[Document] = get_file_documents(path)

                # 如果文件无有效文本内容，跳过
                if not documents:
                    logger.warning(f"[加载知识库] {path} 无有效文本内容，跳过")
                    continue

                # 第二步：将文档分割为适当大小的文本块
                split_document: list[Document] = self.spliter.split_documents(documents)

                # 如果分片后无内容，跳过
                if not split_document:
                    logger.warning(f"[加载知识库] {path} 分片后无内容，跳过")
                    continue

                # 第三步：将分片后的文档添加到向量数据库中（自动进行向量化）
                self.vector_store.add_documents(split_document)

                # 第四步：保存MD5哈希值，标记该文件已成功加载
                save_md5_hex(md5_hex)

                # 记录成功加载日志
                logger.info(f"[加载知识库] {path} 内容加载成功")
            except Exception as e:
                # 捕获所有异常，exc_info=True会记录详细的错误堆栈信息，便于调试
                logger.error(f"[加载知识库] {path} 加载失败：{str(e)}", exc_info=True)
                continue  # 单个文件加载失败不影响其他文件的处理


# for testing
if __name__ == '__main__':
    store = VectorStoreService()

    store.load_document()

    retriever = store.get_retriever()

    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("-" * 20)
