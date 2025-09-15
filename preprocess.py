from config import AZURE_DEPLOYMENT_MODEL
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

SYNONYM_MAP = {
    "진료항목": "검사항목",
    "검진항목": "검사항목",
    "기관": "센터",
}

client = AzureOpenAI(
    api_version="2024-06-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

def generate_prompt(query, synonym_map):
    mapping = "\n".join([f"'{k}'는 '{v}'로" for k, v in synonym_map.items()])
    return f"""
    다음 문장에서 아래 단어들을 각각 대응하는 단어로 바꾸어 주세요.
    단어 매핑:
    {mapping}
    문장: "{query}"
    문맥이 자연스러운 형태로 변환해 주세요.
    """

def preprocess_query(query):
    prompt = generate_prompt(query, SYNONYM_MAP)
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
