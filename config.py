from dotenv import load_dotenv
import os

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
AZURE_DEPLOYMENT_MODEL = "gpt-4.1-mini"
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INDEX_NAME = "risk-assessment-index"
