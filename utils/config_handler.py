# 导入必要的YAML解析和路径工具模块
import yaml  # YAML文件解析库，用于读取配置文件
from utils.path_tools import get_abs_path  # 路径工具，用于获取配置文件的绝对路径

class ConfigHandler(object):
    """
    配置处理器类，提供静态方法加载各种YAML配置文件。
    使用单例模式的思想，在模块级别预先加载所有配置，避免重复IO操作。
    """
    @staticmethod
    def load_rag_config(config_path: str=get_abs_path("config/rag.yml"), encoding="utf-8"):
        """
        加载RAG相关配置（模型名称等）。
        
        Args:
            config_path (str): RAG配置文件路径，默认为config/rag.yml
            encoding (str): 文件编码，默认UTF-8
            
        Returns:
            dict: 解析后的配置字典
        """
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)  # 使用FullLoader安全加载YAML

    @staticmethod
    def load_chroma_config(config_path: str=get_abs_path("config/chroma.yml"), encoding="utf-8"):
        """
        加载Chroma向量数据库配置（集合名、持久化目录、分片参数等）。
        
        Args:
            config_path (str): Chroma配置文件路径，默认为config/chroma.yml
            encoding (str): 文件编码，默认UTF-8
            
        Returns:
            dict: 解析后的配置字典
        """
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    @staticmethod
    def load_prompts_config(config_path: str=get_abs_path("config/prompts.yml"), encoding="utf-8"):
        """
        加载提示词文件路径配置。
        
        Args:
            config_path (str): 提示词配置文件路径，默认为config/prompts.yml
            encoding (str): 文件编码，默认UTF-8
            
        Returns:
            dict: 解析后的配置字典
        """
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    @staticmethod
    def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding="utf-8"):
        """
        加载Agent相关配置（外部数据路径等）。
        
        Args:
            config_path (str): Agent配置文件路径，默认为config/agent.yml
            encoding (str): 文件编码，默认UTF-8
            
        Returns:
            dict: 解析后的配置字典
        """
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)


# 在模块加载时一次性读取所有配置文件，创建全局配置对象
# 这样避免了每次使用时都读取文件，提高性能
rag_conf = ConfigHandler.load_rag_config()  # RAG配置：包含聊天模型和嵌入模型名称
chroma_conf = ConfigHandler.load_chroma_config()  # Chroma配置：包含数据库参数和分片设置
prompts_conf = ConfigHandler.load_prompts_config()  # 提示词配置：包含各提示词文件路径
agent_conf = ConfigHandler.load_agent_config()  # Agent配置：包含外部数据文件路径
