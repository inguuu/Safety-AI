from config import AZURE_DEPLOYMENT_MODEL
from openai import AzureOpenAI
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, MYSQL_PASSWORD
import pymysql

# SYNONYM_MAP = {
#     ('검진', '검사'),
#  ('검진', '검진'),
#  ('검진', '진료'),
#  ('진료', '검사'),
#  ('진료', '진료'),
#  ('진료', '검진'),
#  ('검사', '검사'),
#  ('검사', '진료'),
#  ('검사', '검진');
# }

client = AzureOpenAI(
    api_version="2024-06-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)


# MySQL 연결 함수
def get_mysql_connection():
    return pymysql.connect(
        host="igigdb01012.mysql.database.azure.com",
        user="jig1135",
        password=MYSQL_PASSWORD,
        database="safety_dev",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# DB에서 synonym map 불러오기
def load_synonym_map():
    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT raw_data, cleaned_data FROM tb_preprocessed")
            rows = cursor.fetchall()

            synonym_dict = {}
            for row in rows:
                raw = row["raw_data"]
                cleaned = row["cleaned_data"]
                if raw not in synonym_dict:
                    synonym_dict[raw] = []
                if cleaned not in synonym_dict[raw]:
                    synonym_dict[raw].append(cleaned)
            return synonym_dict
    finally:
        connection.close()

# OpenAI 프롬프트 생성
def generate_prompt(query, synonym_map):
    mapping = "\n".join([f"'{k}'는 {v} 중 하나로" for k, v in synonym_map.items()])
    return f"""
    다음 문장에서 아래 단어들을 각각 대응하는 단어 중 하나로 바꾸어 주세요.
    단어 매핑:
    {mapping}
    문장: "{query}"
    문맥이 자연스러운 형태로 변환해 주세요.
    """
def preprocess_query(query):
    synonym_map = load_synonym_map()
    prompt = generate_prompt(query, synonym_map)
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()