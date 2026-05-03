# 导入必要的库和模块
import time

import streamlit as st  # Streamlit用于构建Web界面
from agent.react_agent import ReactAgent  # 导入ReAct智能代理类

# 设置页面标题
title = "智扫通机器人智能客服"
st.title(title)
st.divider()  # 添加分隔线

# 初始化会话状态中的消息列表，如果不存在则创建初始欢迎消息
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，我是智扫通机器人智能客服，请问有什么可以帮助你？"}]

# 初始化会话状态中的智能代理实例，如果不存在则创建ReactAgent实例
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

# 显示历史聊天记录，遍历会话状态中的所有消息并展示在页面上
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 在页面最下方提供用户输入栏，等待用户输入问题
prompt = st.chat_input()

# 当用户输入问题后，执行以下逻辑
if prompt:
    # 在页面输出用户的提问内容，以用户角色显示
    st.chat_message("user").write(prompt)
    # 将用户的问题添加到会话状态的消息列表中，用于后续上下文记忆
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []  # 用于存储流式响应的完整内容
    with st.spinner("智能客服思考中..."):  # 显示加载动画提示用户正在处理
        res_stream = st.session_state["agent"].execute_stream(prompt)  # 调用智能代理的流式执行方法

        # 定义一个生成器函数来捕获流式响应并逐字符显示，实现打字机效果
        def capture(generator, cache_list):
            for chunk in generator:  # 遍历流式响应的每个片段
                cache_list.append(chunk)  # 将每个片段缓存到列表中，用于最后保存完整响应
                
                # 逐字符输出以实现打字机效果，每个字符之间延迟0.01秒
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        # 使用stream方法逐字符显示智能客服的回答，同时缓存完整响应内容
        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        # 将完整的助手回复添加到会话状态的消息列表中，保持对话历史完整性
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()  # 重新运行应用以更新界面显示新的消息
