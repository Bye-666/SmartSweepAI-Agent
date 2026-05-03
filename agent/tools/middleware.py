# 导入必要的类型提示和LangChain中间件相关模块
from typing import Callable, Any  # 类型提示：可调用对象和任意类型
from langchain.agents import AgentState  # Agent状态对象，包含消息历史等信息
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest  # 中间件装饰器和请求对象
from langchain.tools.tool_node import ToolCallRequest  # 工具调用请求对象
from langchain_core.messages import ToolMessage  # 工具消息对象，用于封装工具调用结果
from langgraph.runtime import Runtime  # LangGraph运行时对象，包含上下文信息
from langgraph.types import Command  # LangGraph命令类型
from utils.logger_handler import logger  # 日志处理器
from utils.prompt_loader import load_system_prompt, load_report_prompt  # 提示词加载函数


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    """
    工具调用监控中间件：记录工具调用的详细信息，包括工具名称、参数和执行结果。
    该中间件在每次工具调用前后执行，用于调试和监控目的。
    
    Args:
        request (ToolCallRequest): 工具调用请求对象，包含工具名称和参数
        handler (Callable): 实际的工具处理函数
        
    Returns:
        ToolMessage | Command: 工具执行结果或命令对象
        
    Raises:
        Exception: 如果工具调用失败，重新抛出异常
    """
    # 记录正在执行的工具名称
    logger.info(f"[tool monitor]执行工具: {request.tool_call['name']}")
    # 记录工具调用的参数
    logger.info(f"[tool monitor]参数: {request.tool_call['args']}")
    try:
        # 执行实际的工具调用
        result = handler(request)
        # 记录工具调用成功
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        # 特殊处理：如果是fill_context_for_report工具，设置报告生成上下文标志
        if request.tool_call['name'] == 'fill_context_for_report':
            logger.info(f"[tool monitor]fill_context_for_report工具被调用，注入上下文 report=True")
            # 在运行时上下文中设置report标志为True，用于触发动态提示词切换
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        # 如果工具调用失败，记录错误日志并重新抛出异常
        logger.info(f"工具{request.tool_call['name']}调用失败: {e}")
        raise


@before_model
def log_before_model(state:AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    模型调用前日志中间件：在每次调用大语言模型之前记录日志信息。
    该中间件用于调试和追踪Agent的思考过程，记录消息历史和即将发送的内容。
    
    Args:
        state (AgentState): Agent当前状态，包含消息历史等
        runtime (Runtime): LangGraph运行时对象
        
    Returns:
        dict[str, Any] | None: 返回None表示不修改状态，直接继续执行
    """
    # 记录即将调用模型，并显示消息总数
    logger.info(f"[log_before_model]: 即将调用模型，带有{len(state['messages'])}条消息，消息如下：")
    # 注释掉的代码：可以遍历所有消息进行详细记录（为避免日志过多已禁用）
    # for message in state['messages']:
    #     logger.info(f"[log_before_model][{type(message).__name__}]: {message.content.strip()}")
    logger.info(f"[log_before_model]: ----------省略已输出内容----------")
    # 仅记录最后一条消息的内容（通常是最新的用户问题或工具响应）
    logger.info(f"[log_before_model][{type(state['messages'][-1]).__name__}]: {state['messages'][-1].content.strip()}")


    return None  # 返回None表示不修改Agent状态，按原流程继续执行

@dynamic_prompt
def report_prompt_switch(request: ModelRequest) -> str:
    """
    动态提示词切换中间件：根据上下文标志决定使用哪种系统提示词。
    当检测到报告生成场景时，切换到报告专用提示词；否则使用默认系统提示词。
    
    Args:
        request (ModelRequest): 模型请求对象，包含运行时上下文信息
        
    Returns:
        str: 选择的系统提示词文本
    """
    # 从运行时上下文中获取report标志，默认为False（非报告场景）
    is_report = request.runtime.context.get("report", False)
    if is_report:
        # 如果是报告生成场景，加载报告专用提示词
        return load_report_prompt()

    # 否则使用默认的系统提示词
    return load_system_prompt()


