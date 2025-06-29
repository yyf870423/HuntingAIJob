import openai
from app.config import get_config

config = get_config()
OPENAI_API_KEY = config.get("OPENAI_API_KEY", "")
EMBEDDING_MODEL = config.get("EMBEDDING_MODEL", "text-embedding-ada-002")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def call_gpt(prompt, model="gpt-4o-mini", temperature=0.2, max_tokens=4096):
    """
    通用 GPT 调用，返回大模型生成的文本结果。
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def get_embedding_from_llm(text, model=None):
    """
    通用 embedding API 调用，返回文本向量。
    """
    if model is None:
        model = EMBEDDING_MODEL
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

# 可扩展更多 LLM 调用方法，如结构化解析、函数调用等 