"""
API endpoints для группировки СТЕ
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database.base import get_db
from app.models.database import Aggregation, AggregationItem, STE, AggregationRating
from app.models.schemas import (
    GroupingRequest, GroupingResponse, AggregationResponse, AggregationDetailResponse,
    RatingRequest, MessageResponse, AggregationCreate
)
from app.services.grouping_service import GroupingService
from app.config import settings
from app.models.schemas import STEResponse, AggregationItemResponse

router = APIRouter(prefix="/grouping", tags=["Группировка"])


@router.post(
    "/",
    response_model=GroupingResponse,
    summary="Группировка СТЕ",
    description="Осуществляет группировку СТЕ по значимым характеристикам"
)
async def group_stes(
    request: GroupingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Группирует СТЕ по значимым характеристикам.
    
    Если указаны ste_ids - группирует только указанные СТЕ.
    Если указан category_id - группирует СТЕ из этой категории.
    Если указаны characteristics - использует эти характеристики для группировки.
    """
    grouping_service = GroupingService()
    
    # Получаем группы
    groups = await grouping_service.group_stes(
        session=db,
        category_id=request.category_id,
        ste_ids=request.ste_ids,
        similarity_threshold=settings.SIMILARITY_THRESHOLD,
        min_group_size=settings.MIN_GROUP_SIZE,
        max_group_size=settings.MAX_GROUP_SIZE
    )
    
    # Создаем агрегации из групп
    aggregations = []
    total_items = 0
    
    for group_data in groups:
        # Если не требуется перегенерация, проверяем существующие агрегации
        if not request.force_regenerate:
            # Ищем существующую агрегацию
            stmt = (
                select(Aggregation)
                .where(Aggregation.category_id == group_data["category_id"])
                .where(Aggregation.grouping_characteristics == group_data["grouping_characteristics"])
                .where(Aggregation.is_saved == False)
                .options(selectinload(Aggregation.items).selectinload(AggregationItem.ste))
                .limit(1)
            )
            result = await db.execute(stmt)
            existing_agg = result.scalar_one_or_none()
            
            if existing_agg:
                # Загружаем полные данные
                stmt = (
                    select(Aggregation)
                    .where(Aggregation.id == existing_agg.id)
                    .options(selectinload(Aggregation.items).selectinload(AggregationItem.ste))
                )
                result = await db.execute(stmt)
                aggregation = result.scalar_one()
                aggregations.append(aggregation)
                total_items += len(aggregation.items)
                continue
        
        # Создаем новую агрегацию
        aggregation = await grouping_service.create_aggregation_from_group(
            db, group_data, status="auto"
        )
        
        # Загружаем с items
        stmt = (
            select(Aggregation)
            .where(Aggregation.id == aggregation.id)
            .options(selectinload(Aggregation.items).selectinload(AggregationItem.ste))
        )
        result = await db.execute(stmt)
        aggregation = result.scalar_one()
        aggregations.append(aggregation)
        total_items += len(aggregation.items)
    
    # Формируем ответ
    agg_responses = []
    for agg in aggregations:
        items_response = []
        for item in sorted(agg.items, key=lambda x: x.order):
            items_response.append(AggregationItemResponse(
                id=item.id,
                ste=STEResponse.model_validate(item.ste),
                order=item.order,
                created_at=item.created_at
            ))
        
        agg_responses.append(AggregationResponse(
            id=agg.id,
            name=agg.name,
            category_id=agg.category_id,
            grouping_characteristics=agg.grouping_characteristics,
            status=agg.status,
            rating=agg.rating,
            is_saved=agg.is_saved,
            created_at=agg.created_at,
            updated_at=agg.updated_at,
            items=items_response,
            items_count=len(items_response)
        ))
    
    return GroupingResponse(
        aggregations=agg_responses,
        total_groups=len(agg_responses),
        total_items=total_items
    )


@router.get(
    "/aggregations",
    response_model=List[AggregationResponse],
    summary="Список агрегаций",
    description="Возвращает список всех агрегаций"
)
async def list_aggregations(
    category_id: Optional[str] = Query(None, description="Фильтр по категории"),
    saved_only: bool = Query(False, description="Только сохраненные"),
    limit: int = Query(100, ge=1, le=500, description="Лимит результатов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список агрегаций с возможностью фильтрации.
    """
    stmt = select(Aggregation).options(
        selectinload(Aggregation.items).selectinload(AggregationItem.ste)
    )
    
    if category_id:
        stmt = stmt.where(Aggregation.category_id == category_id)
    
    if saved_only:
        stmt = stmt.where(Aggregation.is_saved == True)
    
    stmt = stmt.order_by(Aggregation.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    aggregations = result.scalars().all()
    
    responses = []
    for agg in aggregations:
        items_response = []
        for item in sorted(agg.items, key=lambda x: x.order):
            items_response.append({
                "id": item.id,
                "ste": STEResponse.model_validate(item.ste),
                "order": item.order,
                "created_at": item.created_at
            })
        
        responses.append(AggregationResponse(
            id=agg.id,
            name=agg.name,
            category_id=agg.category_id,
            grouping_characteristics=agg.grouping_characteristics,
            status=agg.status,
            rating=agg.rating,
            is_saved=agg.is_saved,
            created_at=agg.created_at,
            updated_at=agg.updated_at,
            items=items_response,
            items_count=len(items_response)
        ))
    
    return responses


@router.get(
    "/aggregations/{aggregation_id}",
    response_model=AggregationDetailResponse,
    summary="Получить агрегацию",
    description="Возвращает детальную информацию об агрегации"
)
async def get_aggregation(
    aggregation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию об агрегации.
    """
    stmt = (
        select(Aggregation)
        .where(Aggregation.id == aggregation_id)
        .options(selectinload(Aggregation.items).selectinload(AggregationItem.ste))
    )
    result = await db.execute(stmt)
    aggregation = result.scalar_one_or_none()
    
    if not aggregation:
        raise HTTPException(status_code=404, detail=f"Агрегация с ID {aggregation_id} не найдена")
    
    items_response = []
    for item in sorted(aggregation.items, key=lambda x: x.order):
            items_response.append(AggregationItemResponse(
                id=item.id,
                ste=STEResponse.model_validate(item.ste),
                order=item.order,
                created_at=item.created_at
            ))
    
    return AggregationDetailResponse(
        id=aggregation.id,
        name=aggregation.name,
        category_id=aggregation.category_id,
        grouping_characteristics=aggregation.grouping_characteristics,
        status=aggregation.status,
        rating=aggregation.rating,
        is_saved=aggregation.is_saved,
        created_at=aggregation.created_at,
        updated_at=aggregation.updated_at,
        items=items_response
    )

