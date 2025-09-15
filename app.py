from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import streamlit as st;

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
import sys

# .env file 참조
load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
AZURE_DEPLOYMENT_MODEL = "gpt-4.1-mini"  
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

try:
    search_credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)

    openai_client = AzureOpenAI(
        api_version="2024-06-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )

    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name="risk-assessment-index",
        credential=search_credential
    )
    
except ClientAuthenticationError as e:
    print("API KEY를 확인해 주세요")
    sys.exit(1)
except HttpResponseError as e:
    print("엔드포인트를 확인해 주세요")
    sys.exit(1)
except Exception as e:
    print("알 수 없는 오류가 발생했습니다.")
    print(e)
    sys.exit(1)

# 건강검진에 맞는 프롬프트로 변경
GROUNDED_PROMPT = """
You are a friendly and knowledgeable health screening assistant.
Answer the user's query strictly based on the information from the provided sources below.
Use a clear, concise, and friendly style, in bullet points if appropriate.
Do NOT invent any information beyond the sources.
If the information is insufficient, say you don't know.
Query: {query}
Sources:
{sources}
"""


SYNONYM_MAP = {
    "진료항목": "검사항목",
    "검진항목": "검사항목",
    "기관": "센터",
    # 필요시 더 추가
}


def generate_synonym_prompt(raw_query: str, synonym_map: dict) -> str:
    mapping_lines = "\n".join(
        [f"'{k}'는 '{v}'로 변경해주세요." for k, v in synonym_map.items()]
    )
    
    prompt = f"""
    다음 문장에서 아래 단어들을 각각 대응하는 단어로 바꾸어 주세요.
    단어 매핑:
    {mapping_lines}
    문장: "{raw_query}"
    문맥이 자연스러운 형태로 변환해 주세요.
    """
    return prompt


def preprocess_query_with_openai(raw_query: str, synonym_map: dict) -> str:
    prompt = generate_synonym_prompt(raw_query, synonym_map)
    
    response = openai_client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0,
    )
    processed_query = response.choices[0].message.content.strip()
    return processed_query


# LLM 응답 함수 (AISEARCH + GPT 호출 포함)
def get_grounded_response(messages: list):
    user_query = messages[-1]['content']  # 마지막 유저 메시지 기준

    # 1. 전처리해서 유사어 치환
    processed_query = preprocess_query_with_openai(user_query, SYNONYM_MAP)


    # 2. 원본 쿼리와 치환된 쿼리를 모두 포함해서 검색어 구성
    combined_query = f'"{user_query}" OR "{processed_query}"'
    try:
        # Azure Search에서 검색
        search_result = search_client.search(
            search_text=combined_query,
            top=5,
            select="Content,DocumentName,Tags",
        )
        search_results_list = list(search_result)
    except Exception as e:
        return f"검색 오류 발생: {e}"

    # 검색 결과가 없으면 LLM 호출
    if not search_results_list:
        response = openai_client.chat.completions.create(
            model=AZURE_DEPLOYMENT_MODEL,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        llm_answer = response.choices[0].message.content
        if not st.session_state.shown_no_search_msg:
            st.session_state.shown_no_search_msg = True
            return "원하시는 답변을 찾지 못해, 제가 대답해드립니다: " + llm_answer
        else:
            return llm_answer

    sources_formatted = "\n".join([
        f'{doc["DocumentName"]}: {doc["Content"]}: {doc.get("Tags", [])}'
        for doc in search_results_list
    ])

    # GPT 입력 메시지
    messages = [
        {"role": "user",
         "content": GROUNDED_PROMPT.format(query=processed_query, sources=sources_formatted)}
    ]

    # GPT 호출
    response = openai_client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )

    return response.choices[0].message.content


# ------------------------------------------
# 🎨 프론트엔드: Streamlit UI (ChatGPT 스타일)
# ------------------------------------------
st.set_page_config(page_title="건강검진 위험성평가 Agent", page_icon="🩺", layout="centered")

# 💅 스타일: ChatGPT 홈페이지 유사
st.markdown("""
    <style>
        html, body {
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }

        .user-message, .assistant-message {
            padding: 16px;
            border-radius: 12px;
            margin: 16px auto;
            max-width: 700px;
            font-size: 16px;
            line-height: 1.6;
        }

        .user-message {
            background-color: #f1f1f1;
            color: #000;
        }

        .assistant-message {
            background-color: #e8f0fe;
            color: #000;
        }

        .stChatInput input {
            padding: 12px;
            font-size: 16px;
            border-radius: 12px !important;
            border: 1px solid #ccc;
        }

        h1 {
            text-align: center;
            font-weight: 600;
            margin-top: 40px;
            margin-bottom: 20px;
        }

        .stChatMessage {
            display: flex;
            justify-content: center;
        }

        footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# -----------------------
# 🎨 Streamlit UI 디자인
# -----------------------
st.title("🩺 건강검진 위험성평가 Agent")
st.write("<div style='text-align:center;'>건강검진 관련 위험요인을 질문해보세요 🤖</div>", unsafe_allow_html=True)

# 1) 질문 예시 힌트 박스 추가
st.info(
    """
    💡 **질문 예시:**
    - 야간 근무가 건강에 미치는 영향은?
    - 고혈압 위험요인은 무엇인가요?
    - 건강검진에서 꼭 확인해야 하는 항목은?
    """
)

# 2) 질문 가이드 도움말 토글(expander) 추가
with st.expander("❓ 질문 가이드 보기"):
    st.write(
        """
        - **진료항목**, **검진항목** 대신 **검사항목**으로 질문해보세요.
        - 기관 대신 **센터**라는 단어도 사용 가능합니다.
        - 예를 들어, “검진센터의 혈액검사 항목은 무엇인가요?” 처럼 질문해보세요.
        """
    )


# 초기 세션 상태
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'shown_no_search_msg' not in st.session_state:
    st.session_state.shown_no_search_msg = False

# 이전 채팅 메시지 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            f"<div class='{msg['role']}-message'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

user_input_placeholder = (
    "예) 야간 근무가 건강에 미치는 영향은?\n"
    "예) 고혈압 위험요인을 알려줘요\n"
    "예) 건강검진 검사항목에 대해 설명해줘요"
)

# 사용자 입력
if user_input := st.chat_input("예: 야간 근무가 건강에 미치는 영향은?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)

    with st.spinner("🤔 답변을 생성 중입니다..."):
        assistant_response = get_grounded_response(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(f"<div class='assistant-message'>{assistant_response}</div>", unsafe_allow_html=True)