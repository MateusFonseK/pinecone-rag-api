from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # OpenAI settings
    openai_api_key: str
    openai_model: str

    # Pinecone settings
    pinecone_api_key: str
    pinecone_index_name: str

    # R2 settings (optional - for cloud storage)
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket_name: str | None = None

    @property
    def use_r2_storage(self) -> bool:
        return self.r2_access_key_id is not None

    @property
    def storage_type(self) -> str:
        return "r2" if self.r2_access_key_id is not None else "local"

    class Config:
        env_file = ".env"


settings = Settings()