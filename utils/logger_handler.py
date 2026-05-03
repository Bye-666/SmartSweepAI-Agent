# logger_utils.py
# 日志处理模块，提供配置完善的日志器，支持敏感信息脱敏和多级别日志记录
import logging  # Python标准日志库
import os  # 操作系统模块，用于目录操作
import re  # 正则表达式模块，用于敏感信息匹配和替换
from datetime import datetime  # 日期时间模块，用于生成带日期的日志文件名
from typing import Optional  # 可选类型提示
from utils.path_tools import get_abs_path  # 路径工具，获取日志目录的绝对路径

# 日志保存根目录，所有日志文件都存储在此目录下
LOG_ROOT = get_abs_path("logs")
# 确保日志目录存在，如果不存在则创建（exist_ok=True避免已存在时报错）
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志格式配置（包含时间、模块、行号，便于调试Agent）
# 格式说明：时间 - 日志器名称 - 日志级别 - 文件名:行号 - 日志消息
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"  # 日期时间格式：年-月-日 时:分:秒
)


def mask_sensitive_data(text: str) -> str:
    """
    日志脱敏函数：隐藏API Key、手机号、邮箱等敏感信息。
    防止敏感数据泄露到日志文件中，提高系统安全性。
    
    Args:
        text (str): 原始文本内容
        
    Returns:
        str: 脱敏后的文本，敏感信息被替换为星号
    """
    if not isinstance(text, str):
        return text  # 如果不是字符串类型，直接返回

    # 脱敏OpenAI/通义千问API Key（sk-开头，后面跟字母数字下划线）
    text = re.sub(r"sk-\w+", "sk-******", text)
    # 脱敏手机号（1开头，第二位3-9，后面9位数字）
    text = re.sub(r"1[3-9]\d{9}", "1**********", text)
    # 脱敏邮箱（保留用户名前缀和后缀域名，中间部分用****替换）
    text = re.sub(r"(\w+)@(\w+)\.(\w+)", r"\1****@\2.\3", text)
    # 脱敏密码/密钥（password/key/secret=后面的内容替换为******）
    text = re.sub(r"(password|key|secret)=[^& ]+", r"\1=******", text)
    return text


class SensitiveDataFilter(logging.Filter):
    """
    日志过滤器：自动脱敏日志中的敏感信息。
    继承自logging.Filter，在日志记录前对消息内容进行脱敏处理。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤并脱敏日志记录。
        
        Args:
            record (logging.LogRecord): 日志记录对象
            
        Returns:
            bool: 始终返回True，表示允许该日志记录通过
        """
        # 对日志消息脱敏
        if record.msg:
            record.msg = mask_sensitive_data(record.msg)
        # 对日志参数脱敏（如果有）
        if record.args:
            record.args = tuple(mask_sensitive_data(arg) for arg in record.args)
        return True  # 返回True表示允许日志继续处理


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file: Optional[str] = None
) -> logging.Logger:
    """
    获取配置好的日志器（开箱即用）。
    创建的日志器同时输出到控制台和文件，支持不同的日志级别。
    
    Args:
        name (str): 日志器名称（建议按模块命名，如agent.tools/agent.rag/agent.llm）
        console_level (int): 控制台日志级别（默认INFO，开发时可设为DEBUG）
        file_level (int): 文件日志级别（默认DEBUG，记录详细信息）
        log_file (Optional[str]): 自定义日志文件名（默认按日期生成：agent_20240121.log）
        
    Returns:
        logging.Logger: 配置完成的Logger对象
    """
    # 1. 创建/获取日志器
    logger = logging.getLogger(name)  # 根据名称获取或创建日志器
    logger.setLevel(logging.DEBUG)  # 设置全局最低级别为DEBUG，捕获所有级别的日志
    logger.addFilter(SensitiveDataFilter())  # 添加脱敏过滤器，自动脱敏敏感信息

    # 避免重复添加Handler（多次导入时只配置一次）
    if logger.handlers:
        return logger  # 如果已有Handler，说明已配置过，直接返回

    # 2. 配置控制台Handler（开发调试用）
    console_handler = logging.StreamHandler()  # 创建控制台输出处理器
    console_handler.setLevel(console_level)  # 设置控制台日志级别
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)  # 设置日志格式
    logger.addHandler(console_handler)  # 将控制台处理器添加到日志器

    # 3. 配置文件Handler（生产环境留存日志）
    if not log_file:
        # 如果未指定日志文件名，使用默认格式：日志器名称_日期.log
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")  # 创建文件输出处理器
    file_handler.setLevel(file_level)  # 设置文件日志级别
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)  # 设置日志格式
    logger.addHandler(file_handler)  # 将文件处理器添加到日志器

    return logger


# 快捷获取默认Agent日志器
# 在其他模块中可以直接 from utils.logger_handler import logger 使用
logger = get_logger("agent")