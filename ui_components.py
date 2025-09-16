import streamlit as st

def render_examples():
    st.info(
    """
    💡 **질문 예시:**
    - 독감 예방접종을 맞을 수 있는 곳을 알려줘요
    - 위내시경과 대장내시경을 모두 받을 수 있는 센터가 있나요?
    - KMI 광화문센터의 담당자 정보를 알려주세요
    - 고혈압 관련 검사는 어떤 걸 받아야 하나요?
    """
    )


def render_guides():
    with st.expander("❓ 질문 가이드 보기"):
        st.write(
            """
            - 건강검진과 관련된 **위험요인**, **검사 항목**, **센터 정보**, **예약 가능 여부** 등을 자유롭게 질문해보세요.
            - 예를 들어 다음과 같이 질문할 수 있어요:
                - “**독감 예방접종 가능한 센터 알려줘**”
                - “**위내시경 + 대장내시경 가능한 기관 추천해줘**”
                - “**KMI 광화문센터 연락처나 위치가 궁금해요**”
            """
        )

def render_styles():
    st.markdown("""
<style>
/* 기본 채팅 아이콘 숨기기 */
.stChatMessage div[data-testid="stMarkdownContainer"] > div > div:first-child {
    display: none !important;
}

/* 메시지 스타일 조정 (아이콘 대신 이미지 공간 확보) */
.user-message, .assistant-message {
    display: flex;
    align-items: flex-start;
    max-width: 700px;
    padding: 12px 16px;
    border-radius: 12px;
    margin: 16px auto;
    font-size: 16px;
    line-height: 1.6;
}

.user-message img, .assistant-message img {
    width: 32px;
    height: 32px;
    margin-right: 12px;
    border-radius: 50%;
}

/* 말풍선 배경 */
.user-message {
    background-color: #f1f1f1;
    color: #000;
}

.assistant-message {
    background-color: #e8f0fe;
    color: #000;
}
</style>
""", unsafe_allow_html=True)