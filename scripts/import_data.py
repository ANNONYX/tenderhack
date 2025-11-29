"""
Скрипт для первичного импорта данных из Excel файла
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.base import init_db, AsyncSessionLocal
from app.parsers.excel_parser import parse_ste_file
from app.models.database import STE, Category
from app.services.characteristic_analyzer import CharacteristicAnalyzer


async def import_data():
    """Импортирует данные из Excel файла"""
    print("Инициализация базы данных...")
    await init_db()
    
    print("Чтение Excel файла...")
    file_path = Path(__file__).parent.parent / "data" / "Исходные данные_Хакатон_Казань_20251128_1800.xlsx"
    
    if not file_path.exists():
        print(f"Ошибка: Файл не найден: {file_path}")
        return
    
    ste_list = parse_ste_file(str(file_path))
    print(f"Найдено {len(ste_list)} СТЕ в файле")
    
    # Статистика по характеристикам
    with_chars = sum(1 for ste in ste_list if ste.get('characteristics') and len(ste.get('characteristics', {})) > 0)
    without_chars = len(ste_list) - with_chars
    print(f"  - С характеристиками: {with_chars}")
    print(f"  - Без характеристик: {without_chars}")
    
    async with AsyncSessionLocal() as session:
        imported = 0
        updated = 0
        errors = []
        
        # Создаем уникальный список категорий
        categories_map = {}
        
        for ste_data in ste_list:
            try:
                # Добавляем категорию в словарь
                if ste_data.get("category_id") and ste_data.get("category_name"):
                    cat_id = ste_data["category_id"]
                    if cat_id not in categories_map:
                        categories_map[cat_id] = ste_data["category_name"]
                
                # Проверяем, существует ли СТЕ
                from sqlalchemy import select
                stmt = select(STE).where(STE.ste_id == ste_data["ste_id"])
                result = await session.execute(stmt)
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
                    session.add(new_ste)
                    imported += 1
            except Exception as e:
                errors.append(f"Ошибка при импорте СТЕ {ste_data.get('ste_id', 'unknown')}: {str(e)}")
        
        # Создаем категории
        analyzer = CharacteristicAnalyzer()
        for cat_id, cat_name in categories_map.items():
            # Создаем категорию, если её нет
            from sqlalchemy import select
            stmt = select(Category).where(Category.category_id == cat_id)
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                category = Category(
                    category_id=cat_id,
                    name=cat_name,
                    significant_characteristics=[]
                )
                session.add(category)
        
        await session.commit()
        
        print(f"\nИмпорт завершен:")
        print(f"  - Импортировано: {imported}")
        print(f"  - Обновлено: {updated}")
        print(f"  - Ошибок: {len(errors)}")
        
        if errors:
            print("\nПервые 10 ошибок:")
            for error in errors[:10]:
                print(f"  - {error}")
        
        # Анализируем значимые характеристики для категорий
        print("\nАнализ значимых характеристик...")
        for cat_id in categories_map.keys():
            try:
                await analyzer.get_or_create_category_significant_characteristics(
                    session, cat_id, categories_map[cat_id]
                )
                print(f"  - Обработана категория: {categories_map[cat_id]}")
            except Exception as e:
                print(f"  - Ошибка при обработке категории {cat_id}: {e}")


if __name__ == "__main__":
    asyncio.run(import_data())

