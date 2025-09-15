from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, INDEX_NAME

client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

def search_documents(query):
    try:
        results = client.search(
            search_text=query,
            top=5,
            select="Content,DocumentName,Tags"
        )
        return list(results)
    except Exception as e:
        print(f"[Search Error]: {e}")
        return []
