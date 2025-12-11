from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # OpenAI settings
    openai_api_key: str
    openai_model: str 

    # Pinecone settings
    pinecone_api_key: str
    pinecone_index_name: str 

    class Config:
        env_file = ".env"


settings = Settings()