from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    
    APP_NAME: str = "KAG Learning Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", env="NEO4J_PASSWORD")
    NEO4J_DATABASE: str = Field(default="neo4j", env="NEO4J_DATABASE")
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=50, env="NEO4J_MAX_CONNECTION_POOL_SIZE")
    
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama3-70b-8192", env="GROQ_MODEL")
    GROQ_MAX_TOKENS: int = Field(default=2048, env="GROQ_MAX_TOKENS")
    GROQ_TEMPERATURE: float = Field(default=0.1, env="GROQ_TEMPERATURE")
    
    SPARK_APP_NAME: str = "KAG_Analytics"
    SPARK_MASTER: str = Field(default="local[*]", env="SPARK_MASTER")
    SPARK_DRIVER_MEMORY: str = Field(default="4g", env="SPARK_DRIVER_MEMORY")
    
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost"],
        env="CORS_ORIGINS")
    
    MAX_DEPENDENCY_DEPTH: int = Field(default=10, env="MAX_DEPENDENCY_DEPTH")
    MIN_MASTERY_THRESHOLD: float = Field(default=0.7, env="MIN_MASTERY_THRESHOLD")
    GAP_SIGNIFICANCE_THRESHOLD: float = Field(default=0.3, env="GAP_SIGNIFICANCE_THRESHOLD")
    
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
