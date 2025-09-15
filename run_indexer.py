# python run_indexer.py

from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient

# 환경변수 로드
load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

indexer_name = "safetyindexer01"  # 실행할 인덱서 이름

# 인증 및 클라이언트 생성
credential = AzureKeyCredential(search_api_key)
indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=credential)

# 인덱서 실행
try:
    indexer_client.run_indexer(indexer_name)
    print(f"Indexer '{indexer_name}' is running to index blob data.")
except Exception as e:
    print(f"Error running indexer: {e}")
