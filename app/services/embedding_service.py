from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"

def generate_embedding(text: str) -> list[float]:
    """
    Embeds a text using the OpenAI API.
    """
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding