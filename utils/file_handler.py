# 导入必要的哈希、操作系统和LangChain文档加载模块
import hashlib  # 哈希算法库，用于计算文件MD5值
import os  # 操作系统模块，提供文件和目录操作功能
from typing import Optional  # 可选类型提示

from langchain_core.documents import Document  # LangChain文档对象
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader  # LangChain文档加载器


def get_file_md5_hex(filepath: str) -> Optional[str]:
    """
    计算文件的MD5哈希值，返回十六进制字符串。
    MD5用于唯一标识文件内容，检测文件是否发生变化，避免重复加载相同文件。
    
    Args:
        filepath (str): 文件的绝对/相对路径
        
    Returns:
        Optional[str]: 成功返回32位MD5十六进制字符串，失败返回None
    """
    # 1. 校验文件是否存在
    if not os.path.exists(filepath):
        print(f"错误：文件 {filepath} 不存在")
        return None

    # 2. 校验是否是文件（避免传入文件夹路径）
    if not os.path.isfile(filepath):
        print(f"错误：{filepath} 不是有效文件")
        return None

    # 3. 初始化MD5对象
    md5_obj = hashlib.md5()

    # 4. 分片读取大文件（避免一次性加载占满内存）
    chunk_size = 4096  # 4KB分片，可根据需求调整，平衡内存使用和IO效率
    try:
        with open(filepath, "rb") as f:  # 必须以二进制模式打开文件
            while chunk := f.read(chunk_size):  # 逐片读取，直到文件末尾
                md5_obj.update(chunk)  # 更新MD5摘要，累积计算哈希值

        # 5. 获取十六进制字符串（32位小写）
        md5_hex = md5_obj.hexdigest()
        return md5_hex

    except PermissionError:
        # 处理文件权限不足的情况
        print(f"错误：无权限读取文件 {filepath}")
        return None
    except Exception as e:
        # 处理其他可能的异常（如IO错误等）
        print(f"计算MD5失败：{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """
    列出指定目录下符合允许类型的文件列表。
    
    Args:
        path (str): 要扫描的目录路径
        allowed_types (tuple[str]): 允许的文件扩展名元组，如("txt", "pdf", "csv")
        
    Returns:
        tuple[str]: 符合条件的文件完整路径元组
    """
    files = []  # 存储符合条件的文件路径
    print("x2:", allowed_types, type(allowed_types))  # 调试输出：显示允许的类型
    
    # 验证路径是否为有效目录
    if not os.path.isdir(path):
        print(f"错误：{path} 不是有效目录或不存在")
        return tuple(files)

    # 遍历目录下的所有文件和子目录
    for f in os.listdir(path):
        print("x1: ", f)  # 调试输出：显示当前检查的文件名
        # 检查文件扩展名是否在允许的列表中
        if f.endswith(allowed_types):
            print("x2: ", f)  # 调试输出：显示匹配的文件
            files.append(os.path.join(path, f))  # 将完整路径添加到结果列表

    return tuple(files)  # 返回元组形式的文件路径列表


def csv_loader(filepath: str, source_column=None, encoding='utf-8', csv_args=None) -> list[Document]:
    """
    加载CSV文件为LangChain文档列表。
    
    Args:
        filepath (str): CSV文件路径
        source_column: 源列名，用于标记文档来源（可选）
        encoding (str): 文件编码，默认UTF-8
        csv_args: CSV解析参数（可选）
        
    Returns:
        list[Document]: 解析后的文档列表，每行数据转换为一个文档
    """
    # 创建CSV加载器实例
    loader = CSVLoader(
        filepath,
        source_column=source_column,
        encoding=encoding,
        csv_args=csv_args,
    )
    return loader.load()  # 加载并返回文档列表


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    """
    加载PDF文件为LangChain文档列表。
    
    Args:
        filepath (str): PDF文件路径
        passwd: PDF密码，用于加密的PDF文件（可选）
        
    Returns:
        list[Document]: 解析后的文档列表，每页内容转换为一个文档
    """
    # 创建PDF加载器实例并加载内容
    return PyPDFLoader(filepath, passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    """
    加载纯文本文件为LangChain文档列表。
    
    Args:
        filepath (str): TXT文件路径
        
    Returns:
        list[Document]: 解析后的文档列表，整个文件内容通常作为一个文档
    """
    # 创建文本加载器实例并加载内容
    return TextLoader(filepath).load()
