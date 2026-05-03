# 导入必要的LangChain工具和自定义模块
from langchain_core.tools import tool  # LangChain的装饰器，用于将函数转换为工具
from langgraph.prebuilt.tool_node import ToolCallRequest  # 工具调用请求对象

from rag.vector_store import VectorStoreService  # 向量存储服务
from rag.rag_service import RagSummarizeService  # RAG总结服务
import random, os  # 随机数模块和操作系统模块
from utils.config_handler import agent_conf  # Agent配置文件
from utils.path_tools import get_abs_path  # 路径工具
from utils.logger_handler import logger  # 日志处理器


# 初始化全局向量存储和RAG服务实例（单例模式）
# 这些服务在应用启动时创建一次，所有工具函数共享使用
vector_store = VectorStoreService()  # 创建向量存储服务实例
rag = RagSummarizeService(vector_store)  # 创建RAG总结服务实例，依赖向量存储服务

# 模拟用户ID列表，用于get_user_id工具返回随机用户ID
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
# 模拟月份数组，用于get_current_month工具返回随机月份（格式：YYYY-MM）
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

# 外部数据缓存字典，用于存储从CSV文件加载的用户使用记录
# 结构：{user_id: {month: {特征, 效率, 耗材, 对比}}}
external_data = {}

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    """
    RAG总结工具：基于向量检索和LLM生成专业回答。
    
    Args:
        query (str): 检索查询词，通常是用户问题或关键词
        
    Returns:
        str: 基于检索资料生成的总结回答
    """
    return rag.rag_summarize(query)  # 调用RAG服务执行检索和总结


@tool(description="获取指定城市的天气，以消息字符形式返回")
def get_weather(city: str) -> str:
    """
    天气查询工具：返回指定城市的模拟天气信息。
    注意：当前为模拟数据，实际应用中应接入真实天气API。
    
    Args:
        city (str): 城市名称
        
    Returns:
        str: 包含天气、温度、湿度、风向、AQI和降雨概率的天气信息字符串
    """
    # 返回固定的模拟天气数据（实际项目应替换为真实API调用）
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时内降雨概率极低"


@tool(description="获取用户所在城市名称，以纯字符形式返回")
def get_user_location() -> str:
    """
    用户位置获取工具：随机返回一个模拟城市名称。
    注意：当前为模拟数据，实际应用中应从用户会话或地理位置服务获取。
    
    Returns:
        str: 城市名称（从深圳、合肥、杭州中随机选择）
    """
    return random.choice(["深圳", "合肥", "杭州"])  # 从预设城市列表中随机选择一个


@tool(description="获取用户ID，以纯字符形式返回")
def get_user_id() -> str:
    """
    用户ID获取工具：随机返回一个模拟用户ID。
    注意：当前为模拟数据，实际应用中应从用户认证系统获取真实用户ID。
    
    Returns:
        str: 用户ID字符串（从1001-1010中随机选择）
    """
    return random.choice(user_ids)  # 从预设用户ID列表中随机选择一个


@tool(description="获取当前月份，以纯字符形式返回")
def get_current_month() -> str:
    """
    当前月份获取工具：随机返回一个模拟月份。
    注意：当前为模拟数据，实际应用中应使用datetime获取真实当前月份。
    
    Returns:
        str: 月份字符串，格式为YYYY-MM（从2025年各月中随机选择）
    """
    return random.choice(month_arr)  # 从预设月份列表中随机选择一个


def generate_external_data():
    """
    加载外部数据文件（CSV格式）到内存缓存中。
    该函数采用懒加载策略，仅在首次调用时读取文件，后续调用直接使用缓存。
    
    CSV文件格式预期：user_id,feature,efficiency,consumables,comparison,time
    
    Raises:
        KeyError: 当配置中缺少external_data_path字段时
        FileNotFoundError: 当外部数据文件不存在时
    """
    # 检查缓存是否为空，避免重复加载文件
    if not external_data:
        # 验证配置中是否包含外部数据文件路径
        if "external_data_path" not in agent_conf:
            raise KeyError("配置中缺少 external_data_path 字段")

        # 获取外部数据文件的绝对路径
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        # 验证文件是否存在
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件不存在: {external_data_path}")

        # 读取CSV文件并解析数据
        with open(external_data_path, "r", encoding="utf-8") as f:
            # 跳过标题行（[1:]），逐行处理数据
            for line in f.readlines()[1:]:
                # 按逗号分割每行数据
                arr = line.strip().split(",")

                # 提取各个字段并去除引号
                user_id = arr[0].replace('"', "")  # 用户ID
                feature = arr[1].replace('"', "")  # 特征
                efficiency = arr[2].replace('"', "")  # 效率
                consumables = arr[3].replace('"', "")  # 耗材
                comparison = arr[4].replace('"', "")  # 对比
                time = arr[5].replace('"', "")  # 时间（月份）

                # 如果该用户ID尚未在缓存中，创建新的用户记录字典
                if user_id not in external_data:
                    external_data[user_id] = {}

                # 为该用户在指定月份下存储使用记录
                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }



@tool(description="检索指定用户在指定月份的扫地/扫拖机器人完整使用记录，以纯字符形式返回，如未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    """
    外部数据检索工具：获取指定用户在指定月份的扫地机器人使用记录。
    
    Args:
        user_id (str): 用户ID，如"1001"
        month (str): 月份，格式为YYYY-MM，如"2025-06"
        
    Returns:
        str: 包含特征、效率、耗材、对比等信息的使用记录字典，未找到则返回空字符串
    """
    # 确保外部数据已加载到缓存中（首次调用时会加载）
    generate_external_data()
    try:
        # 从缓存中获取指定用户和月份的数据
        return external_data[user_id][month]
    except KeyError:
        # 如果用户ID或月份不存在，记录警告日志并返回空字符串
        logger.warn(f"[fetch_external_data]未能检索到用户:{user_id}在{month}的数据。")
        return ""


@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成场景动态注入上下文信息，为后续提示词切换提供上下文支撑")
def fill_context_for_report():
    """
    报告上下文填充工具：标记当前为报告生成场景。
    该工具本身不返回有用数据，其主要作用是通过中间件设置上下文标志，
    触发动态提示词切换机制，使Agent切换到报告生成专用的提示词。
    
    Returns:
        str: 固定返回消息，表示工具已调用
    """
    return "fill_context_for_report已调用"
