from openai import OpenAI
import streamlit as st
import pandas as pd
import time
import os

assistant_id = "asst_GwRek9mA8y7YCDMoysGV9nb6"
openai_api_key = os.getenv('OPENAI_API_KEY')

# 스레드 ID를 저장하고 관리하기 위한 session_state 초기화
if "thread_id" not in st.session_state:
    st.session_state.thread_id = ""
    
with st.sidebar:
        
    #thread_id = st.text_input("Thread ID")

    thread_btn = st.button("스레드를 만들어 대화를 시작합니다.")
    
    client = OpenAI(api_key=openai_api_key)
    
    if thread_btn:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.subheader(f"{st.session_state.thread_id}", divider="rainbow")
        st.info("스레드가 생성되었습니다! 이제 대화를 시작해보세요.")
    
    thread_id = st.session_state.thread_id

st.title("💬 새싹이")
st.caption("쳇봇을 통해 농촌진흥청 담당자를 찾아보세요.")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 무엇이 궁금하신가요?"},
    {"role": "assistant", "content": "왼쪽 위에 ' > '를 눌러 스레드를 생성하고 문의사항을 입력해주세요."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("진행하시려면 OpenAI API key가 필요합니다.")
        st.stop()

    if not thread_id:
        st.info("진행하시려면 thread ID가 필요합니다.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=prompt,
        )
    print(response)

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
        )
    print(run)

    run_id = run.id

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
            )
        if run.status == "completed":
            break
        else:
            with st.spinner("자료를 검토중입니다"):
                time.sleep(1)
            st.experimental_rerun()  # 이전에 출력된 내용이 반복해서 나타나는 문제를 방지
    st.write(run)

    thread_messages = client.beta.threads.messages.list(thread_id)
    print(thread_messages.data)

    msg = thread_messages.data[0].content[0].text.value
    print(msg)

    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
