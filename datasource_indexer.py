# python datasource_indexer.py

from dotenv import load_dotenv
import os
import time
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceType,
    SearchIndexerSkillset,
    OcrSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry
)

# 환경변수 로드
load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
storage_key = os.getenv("AZURE_STORAGE_KEY")
index_name = "risk-assessment-index"

credential = AzureKeyCredential(search_api_key)
indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=credential)

# 1. DataSource 생성 (Blob Storage) 이걸로 만들면 안됨
data_source_name = "risk-datasource3"
container_name = "margies"

data_source = SearchIndexerDataSourceConnection(
    name=data_source_name,
    type=SearchIndexerDataSourceType.AZURE_BLOB,
    connection_string=f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={storage_key};EndpointSuffix=core.windows.net",
    container=SearchIndexerDataContainer(name=container_name)
)

indexer_client.create_or_update_data_source_connection(data_source)
print(f"DataSource '{data_source_name}' created or updated.")

# 2. Skillset 생성 (PDF 이미지 OCR 포함)
skillset_name = "risk-pdf-skillset"
ocr_skill = OcrSkill(
    name="pdf-ocr",
    description="Extract text from images in PDF",
    context="/document",
    inputs=[InputFieldMappingEntry(name="image", source="/document/content")],
    outputs=[OutputFieldMappingEntry(name="text", target_name="extracted_text")]
)
skillset = SearchIndexerSkillset(
    name=skillset_name,
    description="Extract text from PDF files including images",
    skills=[ocr_skill]
)
indexer_client.create_or_update_skillset(skillset)
print(f"Skillset '{skillset_name}' created or updated.")

# 3. Indexer 생성 (Blob → Index 자동 매핑, Skillset 적용)
indexer_name = "risk-indexer23333"
indexer = SearchIndexer(
    name=indexer_name,
    data_source_name="risk0101",
    target_index_name="risk-assessment-index",
    skillset_name="risk-pdf-skillset",  # OCR 스킬셋 연결
    schedule=None
)

indexer_client.create_or_update_indexer(indexer)
print(f"Indexer '{indexer_name}' created or updated.")

# 4. Indexer 실행 (즉시 실행)
indexer_client.run_indexer(indexer_name)
print(f"Indexer '{indexer_name}' is running to index blob data.")