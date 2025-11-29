"""
SQLAlchemy модели для базы данных
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class STE(Base):
    """Модель стандартной товарной единицы"""
    __tablename__ = "ste"
    
    id = Column(Integer, primary_key=True, index=True)
    ste_id = Column(String, unique=True, nullable=False, index=True, comment="ID СТЕ из исходных данных")
    name = Column(String, nullable=False, index=True, comment="Название СТЕ")
    image_url = Column(String, comment="Ссылка на картинку")
    model = Column(String, comment="Модель")
    country = Column(String, comment="Страна происхождения")
    manufacturer = Column(String, comment="Производитель")
    category_id = Column(String, index=True, comment="ID категории")
    category_name = Column(String, index=True, comment="Название категории")
    characteristics = Column(JSON, comment="Характеристики в виде JSON")
    characteristics_raw = Column(Text, comment="Сырые характеристики из Excel")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    aggregation_items = relationship("AggregationItem", back_populates="ste", cascade="all, delete-orphan")


class Category(Base):
    """Модель категории товаров"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String, unique=True, nullable=False, index=True, comment="ID категории")
    name = Column(String, nullable=False, index=True, comment="Название категории")
    significant_characteristics = Column(JSON, comment="Значимые характеристики для категории")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Aggregation(Base):
    """Модель агрегации (группы СТЕ)"""
    __tablename__ = "aggregations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment="Название агрегации")
    category_id = Column(String, ForeignKey("categories.category_id"), index=True)
    grouping_characteristics = Column(JSON, comment="Характеристики, по которым проводилась группировка")
    status = Column(String, default="auto", comment="auto - автоматическая, manual - ручная")
    rating = Column(Float, comment="Оценка агрегации")
    is_saved = Column(Boolean, default=False, comment="Сохранена ли агрегация")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    items = relationship("AggregationItem", back_populates="aggregation", cascade="all, delete-orphan")
    ratings = relationship("AggregationRating", back_populates="aggregation", cascade="all, delete-orphan")


class AggregationItem(Base):
    """Связь между агрегацией и СТЕ"""
    __tablename__ = "aggregation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    aggregation_id = Column(Integer, ForeignKey("aggregations.id"), nullable=False, index=True)
    ste_id = Column(Integer, ForeignKey("ste.id"), nullable=False, index=True)
    order = Column(Integer, default=0, comment="Порядок в группе")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    aggregation = relationship("Aggregation", back_populates="items")
    ste = relationship("STE", back_populates="aggregation_items")


class AggregationRating(Base):
    """Оценка агрегации пользователем"""
    __tablename__ = "aggregation_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    aggregation_id = Column(Integer, ForeignKey("aggregations.id"), nullable=False, index=True)
    rating = Column(Float, nullable=False, comment="Оценка от 1 до 5")
    comment = Column(Text, comment="Комментарий к оценке")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    aggregation = relationship("Aggregation", back_populates="ratings")

