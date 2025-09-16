from openai import AzureOpenAI
from config import AZURE_DEPLOYMENT_MODEL, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

client = AzureOpenAI(
    api_version="2024-06-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

STYLE_INSTRUCTIONS = {
    "정확도 우선": "Answer precisely and with high accuracy based strictly on the sources.",
    "빠르게": "Provide a concise and quick answer focusing on key points.",
    "간략하게": "Summarize the answer briefly with only the essential information.",
    "상세하게": "Explain in detail, covering all relevant aspects thoroughly."
}

STYLE_PARAMETERS = {
    "정확도 우선":   {"temperature": 0.2, "top_p": 0.7, "max_tokens": 800},
    "빠르게":       {"temperature": 0.2, "top_p": 0.7, "max_tokens": 300},
    "간략하게":     {"temperature": 0.3, "top_p": 0.7, "max_tokens": 400},
    "상세하게":     {"temperature": 0.7, "top_p": 0.9, "max_tokens": 1200},
}

def get_grounded_answer(query, docs, style="정확도 우선"):

    style_instruction = STYLE_INSTRUCTIONS.get(style, "")
    style_params = STYLE_PARAMETERS.get(style, {"temperature": 0.2, "top_p": 0.7, "max_tokens": 800})

    sources = "\n".join([
        f"{doc['DocumentName']}: {doc['Content']}: {doc.get('Tags', [])}"
        for doc in docs
    ])

    prompt = f"""
        You are a friendly and knowledgeable health screening assistant.
        {style_instruction}
        Answer the user's query strictly based on the information from the provided sources below.
        Use a clear, concise, and friendly style, in bullet points if appropriate.
        Do NOT invent any information beyond the sources.
        If the information is insufficient, say you don't know.
        Query: {query}
        Sources:
        {sources}
        """

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=style_params["temperature"],
        top_p=style_params["top_p"],
        max_tokens=style_params["max_tokens"]
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
