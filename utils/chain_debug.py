# 调试工具模块，用于打印和记录LangChain提示词内容


def print_prompt(prompt, logger=None):
    """
    打印提示词内容，用于调试目的。
    可以选择输出到控制台或记录到日志文件。
    
    Args:
        prompt: LangChain提示词对象，必须有to_string()方法
        logger: 日志处理器对象（可选），如果提供则记录到日志，否则打印到控制台
        
    Returns:
        返回原始prompt对象，支持链式调用
    """
    if logger:
        # 如果提供了日志处理器，将提示词内容记录到日志
        logger.info(f"[print_prompt]" + "==========")
        logger.info(f"{prompt.to_string()}")  # 调用to_string()获取提示词的文本表示
        logger.info(f"[print_prompt]" + "==========")
    else:
        # 否则直接打印到控制台
        print(f"[print_prompt]" + "==========")
        print(f"{prompt.to_string()}")
        print(f"[print_prompt]" + "==========")

    return prompt  # 返回原始对象，支持链式调用
