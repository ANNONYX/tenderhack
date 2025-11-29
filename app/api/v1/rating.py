"""
API endpoints для оценки агрегаций
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database.base import get_db
from app.models.database import Aggregation, AggregationRating
from app.models.schemas import RatingRequest, MessageResponse

router = APIRouter(prefix="/ratings", tags=["Оценки"])


@router.post(
    "/aggregations/{aggregation_id}",
    response_model=MessageResponse,
    summary="Поставить оценку агрегации",
    description="Позволяет пользователю поставить оценку агрегации от 1 до 5"
)
async def rate_aggregation(
    aggregation_id: int,
    request: RatingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ставит оценку агрегации.
    
    Оценка может быть от 1 до 5.
    """
    # Проверяем существование агрегации
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Создаем оценку
    rating = AggregationRating(
        aggregation_id=aggregation_id,
        rating=request.rating,
        comment=request.comment
    )
    db.add(rating)
    
    # Обновляем среднюю оценку агрегации
    stmt = select(func.avg(AggregationRating.rating)).where(
        AggregationRating.aggregation_id == aggregation_id
    )
    result = await db.execute(stmt)
    avg_rating = result.scalar()
    
    if avg_rating:
        aggregation.rating = round(float(avg_rating), 2)
    
    await db.commit()
    
    return MessageResponse(message=f"Оценка {request.rating} успешно поставлена агрегации {aggregation_id}")


@router.get(
    "/aggregations/{aggregation_id}",
    response_model=dict,
    summary="Получить оценки агрегации",
    description="Возвращает все оценки для агрегации"
)
async def get_aggregation_ratings(
    aggregation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все оценки агрегации.
    """
    # Проверяем существование агрегации
    stmt = select(Aggregation).where(Aggregation.id == aggregation_id)
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    # Получаем все оценки
    stmt = select(AggregationRating).where(
        AggregationRating.aggregation_id == aggregation_id
    ).order_by(AggregationRating.created_at.desc())
    
    result = await db.execute(stmt)
    ratings = result.scalars().all()
    
    ratings_list = [
        {
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat()
        }
        for r in ratings
    ]
    
    return {
        "aggregation_id": aggregation_id,
        "average_rating": aggregation.rating,
        "ratings_count": len(ratings_list),
        "ratings": ratings_list
    }

