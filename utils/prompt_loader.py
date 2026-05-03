# 导入配置、路径和日志模块
from utils.config_handler import prompts_conf  # 提示词配置文件，包含各提示词文件的路径
from utils.path_tools import get_abs_path  # 路径工具，用于获取提示词文件的绝对路径
from utils.logger_handler import logger  # 日志处理器，记录加载过程中的错误信息


def load_system_prompt():
    """
    加载主系统提示词，定义Agent的核心行为准则和能力范围。
    该提示词指导Agent如何思考、何时调用工具、如何处理报告生成等场景。
    
    Returns:
        str: 主系统提示词的完整文本内容
        
    Raises:
        KeyError: 当配置中缺少main_prompt_path字段时
        FileNotFoundError: 当提示词文件不存在时
        Exception: 其他读取文件时的异常
    """
    try:
        # 从配置中获取主提示词文件路径并转换为绝对路径
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])
    except KeyError as e:
        # 如果配置中缺少路径字段，记录错误并抛出异常
        logger.error(f"[load_system_prompt]解析系统提示词文件路径失败。")
        raise e

    try:
        # 以UTF-8编码读取提示词文件全部内容
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except FileNotFoundError as e:
        # 文件不存在时记录详细错误信息
        logger.error(f"[load_system_prompt]系统提示词文件{system_prompt_path}不存在. {str(e)}")
        raise e
    except Exception as e:
        # 捕获其他可能的异常（如权限错误、编码错误等）
        logger.error(f"[load_system_prompt]解析系统提示词{system_prompt_path}失败. {str(e)}")
        raise e


def load_report_prompt():
    """
    加载报告生成专用提示词，用于指导Agent生成用户使用情况报告。
    当检测到报告生成场景时，Agent会切换到此提示词。
    
    Returns:
        str: 报告生成提示词的完整文本内容
        
    Raises:
        KeyError: 当配置中缺少report_prompt_path字段时
        FileNotFoundError: 当提示词文件不存在时
        Exception: 其他读取文件时的异常
    """
    try:
        # 从配置中获取报告提示词文件路径并转换为绝对路径
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])
    except KeyError as e:
        # 如果配置中缺少路径字段，记录错误并抛出异常
        logger.error(f"[report_prompt_path]解析系统提示词文件路径失败。")
        raise e

    try:
        # 以UTF-8编码读取提示词文件全部内容
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except FileNotFoundError as e:
        # 文件不存在时记录详细错误信息
        logger.error(f"[report_prompt_path]报告提示词文件{report_prompt_path}不存在. {str(e)}")
        raise e
    except Exception as e:
        # 捕获其他可能的异常
        logger.error(f"[report_prompt_path]解析报告提示词{report_prompt_path}失败. {str(e)}")
        raise e
