from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tabayun Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = ""
    
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = ""
    EMBEDDING_MODEL: str = ""
    OPENAI_API_KEY: str = ""

    
    RESEND_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
