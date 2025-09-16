import streamlit as st
from preprocess import preprocess_query
from search_handler import search_documents
from llm_handler import get_grounded_answer, fallback_answer
from ui_components import render_examples, render_guides, render_styles

# Streamlit 기본 설정
st.set_page_config(page_title="건강검진 안내 Agent", page_icon="💙", layout="centered")

# 상단 로고 + 제목 구성
col1, col2 = st.columns([1, 5])

with col1:
    st.image("data/healthy.png", width=60)

with col2:
    st.markdown("""
    <div style="display: flex; align-items: center; height: 60px;">
        <h1 style="margin: 0; padding-left: 8px;">건강검진 안내 AGENT</h1>
    </div>
    """, unsafe_allow_html=True)
render_styles()
render_examples()
render_guides()

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'shown_no_search_msg' not in st.session_state:
    st.session_state.shown_no_search_msg = False

# 이전 채팅 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<div class='{msg['role']}-message'>{msg['content']}</div>", unsafe_allow_html=True)

# 사용자 입력
if user_input := st.chat_input("건강검진에 대해 무엇이든 물어보세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("🤔 답변을 생성 중입니다..."):
        processed_query = preprocess_query(user_input)
        combined_query = f'"{user_input}" OR "{processed_query}"'
        docs = search_documents(combined_query)

        if docs:
            response = get_grounded_answer(processed_query, docs)
        else:
            response = fallback_answer(st.session_state.messages)
            if not st.session_state.shown_no_search_msg:
                response = "원하시는 답변을 찾지 못해, 제가 대답해드립니다: " + response
                st.session_state.shown_no_search_msg = True

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
