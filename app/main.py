"""
Главный файл FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.base import init_db
from app.api.v1 import ste, grouping, aggregation_edit, rating
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных инициализирована")


@app.get("/", tags=["Главная"])
async def root():
    """
    Главная страница API.
    """
    return {
        "message": "Добро пожаловать в сервис группировки СТЕ",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }


@app.get("/health", tags=["Здоровье"])
async def health_check():
    """
    Проверка здоровья сервиса.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION
    }


# Подключаем роутеры
app.include_router(ste.router, prefix=settings.API_V1_PREFIX)
app.include_router(grouping.router, prefix=settings.API_V1_PREFIX)
app.include_router(aggregation_edit.router, prefix=settings.API_V1_PREFIX)
app.include_router(rating.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

