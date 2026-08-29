# Arquivo: backend/core/config.py

import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field

class Settings(BaseSettings):
    RATE_LIMIT_PER_MINUTE: int = Field(default=30)

class Settings(BaseSettings):
    """
    Configurações da aplicação, carregadas de variáveis de ambiente.
    """
    # --- Configuração Geral ---
    ENV: str = "development"

    # --- API do Gemini ---
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash-latest"

    # --- Backend e Modelos de RAG ---
    EMBEDDING_MODEL: str = "rufimelo/Legal-BERTimbau-large"
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    ENABLE_RERANKER: bool = True

    # -- NOVAS CONFIGURAÇÕES DE INGESTÃO --
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

    # --- Serviços (URLs internas do Docker) ---
    QDRANT_URL: str = "http://qdrant:6333"
    REDIS_URL: str = "redis://redis:6379"
    USE_OPENSEARCH: bool = False
    OPENSEARCH_URL: str = "http://opensearch:9200"

    # --- Segurança ---
    JWT_SECRET_KEY: str = "super_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 30

    class Config:
        # O Pydantic-Settings tentará carregar as variáveis de um arquivo .env
        # O caminho é relativo à raiz do projeto, onde o docker-compose é executado
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna uma instância singleton das configurações.
    O lru_cache garante que as configurações sejam carregadas do .env apenas uma vez.
    """
    return Settings()

# Instância global para fácil acesso em outras partes do código
settings = get_settings()