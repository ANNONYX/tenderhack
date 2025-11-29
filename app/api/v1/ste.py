"""
API endpoints для работы со СТЕ
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database.base import get_db
from app.models.database import STE
from app.models.schemas import STEResponse, SearchRequest, SearchResponse
from app.parsers.excel_parser import parse_ste_file
from pathlib import Path

router = APIRouter(prefix="/ste", tags=["СТЕ"])


@router.get(
    "/",
    response_model=SearchResponse,
    summary="Поиск СТЕ",
    description="Осуществляет поиск стандартных товарных единиц по названию, ключевым словам или иным атрибутам"
)
async def search_ste(
    query: Optional[str] = Query(None, description="Поисковый запрос"),
    category_id: Optional[str] = Query(None, description="Фильтр по категории"),
    limit: int = Query(20, ge=1, le=100, description="Лимит результатов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск СТЕ по названию, ключевым словам и другим атрибутам.
    
    Поддерживает поиск по:
    - Названию СТЕ
    - Производителю
    - Модели
    - Категории
    """
    stmt = select(STE)
    
    # Фильтр по категории
    if category_id:
        stmt = stmt.where(STE.category_id == category_id)
    
    # Поиск по запросу
    if query:
        query_lower = query.lower()
        search_filter = or_(
            STE.name.ilike(f"%{query}%"),
            STE.manufacturer.ilike(f"%{query}%"),
            STE.model.ilike(f"%{query}%"),
            STE.category_name.ilike(f"%{query}%")
        )
        stmt = stmt.where(search_filter)
    
    # Получаем общее количество
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Применяем лимит и смещение
    stmt = stmt.order_by(STE.id).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    stes = result.scalars().all()
    
    return SearchResponse(
        items=[STEResponse.model_validate(ste) for ste in stes],
        total=total
    )


@router.get(
    "/{ste_id}",
    response_model=STEResponse,
    summary="Получить СТЕ по ID",
    description="Возвращает информацию о конкретной СТЕ по её ID"
)
async def get_ste(
    ste_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о СТЕ по ID.
    """
    stmt = select(STE).where(STE.id == ste_id)
    result = await db.execute(stmt)
    ste = result.scalar_one_or_none()
    
    if not ste:
        raise HTTPException(status_code=404, detail=f"СТЕ с ID {ste_id} не найдена")
    
    return STEResponse.model_validate(ste)


@router.post(
    "/import",
    response_model=dict,
    summary="Импорт СТЕ из Excel",
    description="Импортирует СТЕ из Excel файла в базу данных"
)
async def import_ste_from_excel(
    file_path: Optional[str] = Query(None, description="Путь к Excel файлу (если не указан, используется файл по умолчанию)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Импортирует СТЕ из Excel файла.
    
    Если путь не указан, используется файл по умолчанию из папки data.
    """
    if not file_path:
        file_path = str(Path(__file__).parent.parent.parent.parent / "data" / "Исходные данные_Хакатон_Казань_20251128_1800.xlsx")
    
    try:
        # Парсим файл
        ste_list = parse_ste_file(file_path)
        
        imported = 0
        updated = 0
        errors = []
        
        for ste_data in ste_list:
            try:
                # Проверяем, существует ли СТЕ
                stmt = select(STE).where(STE.ste_id == ste_data["ste_id"])
                result = await db.execute(stmt)
                existing_ste = result.scalar_one_or_none()
                
                if existing_ste:
                    # Обновляем существующую
                    for key, value in ste_data.items():
                        if hasattr(existing_ste, key):
                            setattr(existing_ste, key, value)
                    updated += 1
                else:
                    # Создаем новую
                    new_ste = STE(**ste_data)
                    db.add(new_ste)
                    imported += 1
            except Exception as e:
                errors.append(f"Ошибка при импорте СТЕ {ste_data.get('ste_id', 'unknown')}: {str(e)}")
        
        await db.commit()
        
        return {
            "message": "Импорт завершен",
            "imported": imported,
            "updated": updated,
            "errors": errors[:10] if errors else []  # Показываем только первые 10 ошибок
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте: {str(e)}")

