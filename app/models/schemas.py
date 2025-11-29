"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


# СТЕ схемы
class STECreate(BaseModel):
    """Создание СТЕ"""
    ste_id: str = Field(..., description="ID СТЕ")
    name: str = Field(..., description="Название СТЕ")
    image_url: Optional[str] = Field(None, description="Ссылка на картинку")
    model: Optional[str] = Field(None, description="Модель")
    country: Optional[str] = Field(None, description="Страна происхождения")
    manufacturer: Optional[str] = Field(None, description="Производитель")
    category_id: Optional[str] = Field(None, description="ID категории")
    category_name: Optional[str] = Field(None, description="Название категории")
    characteristics: Optional[Dict[str, Any]] = Field(None, description="Характеристики")
    characteristics_raw: Optional[str] = Field(None, description="Сырые характеристики")


class STEBase(BaseModel):
    """Базовая схема СТЕ"""
    id: int
    ste_id: str
    name: str
    image_url: Optional[str] = None
    model: Optional[str] = None
    country: Optional[str] = None
    manufacturer: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class STEResponse(STEBase):
    """Ответ с информацией о СТЕ"""
    pass


# Категории
class CategoryBase(BaseModel):
    """Базовая схема категории"""
    id: int
    category_id: str
    name: str
    significant_characteristics: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryResponse(CategoryBase):
    """Ответ с информацией о категории"""
    pass


# Агрегации
class AggregationItemResponse(BaseModel):
    """Элемент агрегации"""
    id: int
    ste: STEResponse
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


class AggregationBase(BaseModel):
    """Базовая схема агрегации"""
    id: int
    name: Optional[str] = None
    category_id: Optional[str] = None
    grouping_characteristics: Optional[Dict[str, Any]] = None
    status: str
    rating: Optional[float] = None
    is_saved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AggregationCreate(BaseModel):
    """Создание агрегации"""
    name: Optional[str] = Field(None, description="Название агрегации")
    category_id: Optional[str] = Field(None, description="ID категории")
    grouping_characteristics: Optional[Dict[str, Any]] = Field(None, description="Характеристики для группировки")
    status: str = Field("auto", description="Статус: auto или manual")


class AggregationResponse(AggregationBase):
    """Ответ с информацией об агрегации"""
    items: List[AggregationItemResponse] = []
    items_count: int = 0


class AggregationDetailResponse(AggregationBase):
    """Детальный ответ об агрегации"""
    items: List[AggregationItemResponse] = []


# Поиск и группировка
class SearchRequest(BaseModel):
    """Запрос на поиск"""
    query: str = Field(..., description="Поисковый запрос")
    category_id: Optional[str] = Field(None, description="Фильтр по категории")
    limit: int = Field(20, ge=1, le=100, description="Лимит результатов")


class GroupingRequest(BaseModel):
    """Запрос на группировку"""
    ste_ids: Optional[List[int]] = Field(None, description="ID СТЕ для группировки (если пусто - все СТЕ)")
    category_id: Optional[str] = Field(None, description="Фильтр по категории")
    characteristics: Optional[Dict[str, Any]] = Field(None, description="Характеристики для группировки")
    force_regenerate: bool = Field(False, description="Принудительно перегенерировать")


class RatingRequest(BaseModel):
    """Запрос на оценку"""
    rating: float = Field(..., ge=1.0, le=5.0, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, description="Комментарий")


# Ответы
class SearchResponse(BaseModel):
    """Ответ на поиск"""
    items: List[STEResponse]
    total: int


class GroupingResponse(BaseModel):
    """Ответ на группировку"""
    aggregations: List[AggregationResponse]
    total_groups: int
    total_items: int


class MessageResponse(BaseModel):
    """Простое сообщение"""
    message: str
    success: bool = True

