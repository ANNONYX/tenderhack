"""
API endpoints для редактирования агрегаций
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database.base import get_db
from app.models.database import Aggregation, AggregationItem, STE
from app.models.schemas import MessageResponse, AggregationDetailResponse, STEResponse, AggregationItemResponse

router = APIRouter(prefix="/aggregations", tags=["Редактирование агрегаций"])


@router.post(
    "/{aggregation_id}/items/{ste_id}",
    response_model=MessageResponse,
    summary="Добавить СТЕ в агрегацию",
    description="Добавляет СТЕ в существующую агрегацию"
)
async def add_ste_to_aggregation(
    aggregation_id: int,
    ste_id: int,
    order: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Добавляет СТЕ в агрегацию.
    """
    # Проверяем существование агрегации
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Проверяем существование СТЕ
    stmt = select(STE).where(STE.id == ste_id)
    result = await db.execute(stmt)
    ste = result.scalar_one_or_none()
    
    if not ste:
        raise HTTPException(status_code=404, detail=f"СТЕ с ID {ste_id} не найдена")
    
    # Проверяем, не добавлена ли уже
    stmt = select(AggregationItem).where(
        AggregationItem.aggregation_id == aggregation_id,
        AggregationItem.ste_id == ste_id
    )
    result = await db.execute(stmt)
    existing_item = result.scalar_one_or_none()
    
    if existing_item:
        raise HTTPException(status_code=400, detail="СТЕ уже добавлена в эту агрегацию")
    
    # Определяем порядок
    if order is None:
        stmt = select(AggregationItem).where(AggregationItem.aggregation_id == aggregation_id)
        result = await db.execute(stmt)
        existing_items = result.scalars().all()
        order = max([item.order for item in existing_items], default=-1) + 1
    
    # Добавляем СТЕ
    item = AggregationItem(
        aggregation_id=aggregation_id,
        ste_id=ste_id,
        order=order
    )
    db.add(item)
    
    # Обновляем статус агрегации на ручную
    aggregation.status = "manual"
    
    await db.commit()
    
    return MessageResponse(message=f"СТЕ {ste_id} успешно добавлена в агрегацию {aggregation_id}")


@router.delete(
    "/{aggregation_id}/items/{item_id}",
    response_model=MessageResponse,
    summary="Удалить СТЕ из агрегации",
    description="Удаляет СТЕ из агрегации"
)
async def remove_ste_from_aggregation(
    aggregation_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удаляет СТЕ из агрегации.
    """
    # Проверяем существование агрегации
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Проверяем существование элемента
    stmt = select(AggregationItem).where(
        AggregationItem.id == item_id,
        AggregationItem.aggregation_id == aggregation_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Элемент с ID {item_id} не найден в агрегации")
    
    # Удаляем элемент (используем delete statement)
    stmt = delete(AggregationItem).where(AggregationItem.id == item_id)
    await db.execute(stmt)
    
    # Обновляем статус агрегации на ручную
    aggregation.status = "manual"
    
    await db.commit()
    
    return MessageResponse(message=f"СТЕ успешно удалена из агрегации {aggregation_id}")


@router.put(
    "/{aggregation_id}/items/{item_id}/order",
    response_model=MessageResponse,
    summary="Изменить порядок СТЕ в агрегации",
    description="Изменяет порядок СТЕ в агрегации"
)
async def change_item_order(
    aggregation_id: int,
    item_id: int,
    new_order: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Изменяет порядок СТЕ в агрегации.
    """
    # Проверяем существование агрегации
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Проверяем существование элемента
    stmt = select(AggregationItem).where(
        AggregationItem.id == item_id,
        AggregationItem.aggregation_id == aggregation_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Элемент с ID {item_id} не найден в агрегации")
    
    # Обновляем порядок
    item.order = new_order
    
    # Обновляем статус агрегации на ручную
    aggregation.status = "manual"
    
    await db.commit()
    
    return MessageResponse(message=f"Порядок СТЕ успешно изменен")


@router.post(
    "/{aggregation_id}/save",
    response_model=MessageResponse,
    summary="Сохранить агрегацию",
    description="Сохраняет агрегацию (помечает как сохраненную)"
)
async def save_aggregation(
    aggregation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Сохраняет агрегацию.
    """
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    aggregation.is_saved = True
    
    await db.commit()
    
    return MessageResponse(message=f"Агрегация {aggregation_id} успешно сохранена")


@router.delete(
    "/{aggregation_id}",
    response_model=MessageResponse,
    summary="Удалить агрегацию",
    description="Удаляет агрегацию"
)
async def delete_aggregation(
    aggregation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удаляет агрегацию.
    """
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Удаляем агрегацию (cascade удалит связанные items)
    stmt = delete(Aggregation).where(Aggregation.id == aggregation_id)
    await db.execute(stmt)
    await db.commit()
    
    return MessageResponse(message=f"Агрегация {aggregation_id} успешно удалена")

