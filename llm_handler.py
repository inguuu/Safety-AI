from openai import AzureOpenAI
from config import AZURE_DEPLOYMENT_MODEL, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

client = AzureOpenAI(
    api_version="2024-06-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

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

def get_grounded_answer(query, docs):
    sources = "\n".join([
        f"{doc['DocumentName']}: {doc['Content']}: {doc.get('Tags', [])}"
        for doc in docs
    ])
    prompt = GROUNDED_PROMPT.format(query=query, sources=sources)

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def fallback_answer(messages):
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()
