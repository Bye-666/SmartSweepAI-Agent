# 导入必要的LangChain和自定义模块
from langchain.agents import create_agent  # LangChain的代理创建函数
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch  # 中间件功能：工具监控、模型调用前日志、报告提示词切换
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
                                     fetch_external_data, fill_context_for_report)  # 各种工具函数定义
from model.factory import chat_model  # 聊天模型工厂，提供大语言模型实例
from utils.prompt_loader import load_system_prompt  # 加载系统提示词的函数


class ReactAgent(object):
    """
    ReAct智能代理类，基于Reasoning and Acting框架实现智能客服功能。
    ReAct框架结合推理(Reasoning)和行动(Acting)，使AI能够进行思考-行动-观察的循环过程。
    """
    def __init__(self):
        """
        初始化ReAct代理，配置模型、系统提示词、工具和中间件。
        """
        # 使用create_agent创建代理实例，传入以下参数：
        self.agent = create_agent(
            model=chat_model,  # 指定使用的聊天模型（通义千问）
            system_prompt=load_system_prompt(),  # 加载主系统提示词，定义代理的行为准则和能力范围
            tools=[rag_summarize, get_weather, get_user_location, get_user_id, get_current_month,
                   fetch_external_data, fill_context_for_report],  # 注册可用工具列表，供代理在需要时调用
            middleware=[monitor_tool, log_before_model, report_prompt_switch],  # 注册中间件，用于工具调用监控、日志记录和动态提示词切换
        )

    def execute_stream(self, query):
        """
        执行流式查询，返回生成器以支持逐字输出效果。
        
        Args:
            query (str): 用户输入的问题或指令
            
        Yields:
            str: 流式输出的文本片段，每个片段末尾添加换行符以便显示
        """
        # 构建输入字典，符合LangChain的消息格式要求
        input_dict = {
            "messages": [
                {"role": "user", "content": query},  # 将用户问题封装为标准消息格式
            ]
        }

        # 使用stream方法进行流式处理，获取代理的逐步响应
        # stream_mode="values"表示返回完整的状态值而非增量更新
        # context={"report": False}设置初始上下文，标记当前不是报告生成场景
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]  # 获取最新消息记录（因为包含历史记录所以取最后一条）
            if latest_message.content:  # 如果消息内容非空，则进行处理
                yield latest_message.content.strip() + "\n"  # 去除首尾空白并添加换行符后产出

if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("扫地机器人在我所在地区的气温下如何保养"):
        print(chunk, end="", flush=True)
