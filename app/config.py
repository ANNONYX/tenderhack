"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # API настройки
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "СТЕ Grouping Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Сервис группировки стандартных товарных единиц по значимым характеристикам"
    
    # База данных
    DATABASE_URL: str = "sqlite+aiosqlite:///./ste_grouping.db"
    
    # Настройки группировки
    MIN_GROUP_SIZE: int = 2  # Минимальный размер группы
    MAX_GROUP_SIZE: int = 50  # Максимальный размер группы
    SIMILARITY_THRESHOLD: float = 0.7  # Порог схожести для группировки
    
    # Настройки ML
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    USE_CUDA: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

