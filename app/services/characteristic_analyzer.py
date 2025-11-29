"""
Сервис для определения значимых характеристик категорий
"""
from typing import List, Dict, Any, Set
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import STE, Category
import re


class CharacteristicAnalyzer:
    """Анализатор значимых характеристик"""
    
    @staticmethod
    def extract_characteristic_keys(all_characteristics: List[Dict[str, Any]]) -> Set[str]:
        """
        Извлекает все уникальные ключи характеристик.
        
        Args:
            all_characteristics: Список словарей характеристик
            
        Returns:
            Множество уникальных ключей
        """
        keys = set()
        for char_dict in all_characteristics:
            if isinstance(char_dict, dict):
                keys.update(char_dict.keys())
        return keys
    
    @staticmethod
    def calculate_characteristic_frequency(
        all_characteristics: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Подсчитывает частоту использования каждой характеристики.
        
        Args:
            all_characteristics: Список словарей характеристик
            
        Returns:
            Словарь {ключ: частота}
        """
        frequency = Counter()
        
        for char_dict in all_characteristics:
            if isinstance(char_dict, dict):
                for key in char_dict.keys():
                    frequency[key] += 1
        
        return dict(frequency)
    
    @staticmethod
    def normalize_characteristic_name(name: str) -> str:
        """
        Нормализует название характеристики для сравнения.
        
        Args:
            name: Название характеристики
            
        Returns:
            Нормализованное название
        """
        # Приводим к нижнему регистру
        normalized = name.lower().strip()
        
        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Убираем знаки препинания в конце
        normalized = normalized.rstrip('.,;:!?')
        
        return normalized
    
    @staticmethod
    def group_similar_characteristics(characteristics: List[str]) -> Dict[str, List[str]]:
        """
        Группирует похожие характеристики (например, "Ширина" и "Ширина профиля").
        
        Args:
            characteristics: Список названий характеристик
            
        Returns:
            Словарь {нормализованное_название: [все_варианты]}
        """
        groups: Dict[str, List[str]] = {}
        normalized_map: Dict[str, str] = {}
        
        for char in characteristics:
            normalized = CharacteristicAnalyzer.normalize_characteristic_name(char)
            
            # Ищем похожие (если нормализованное начинается с другого или наоборот)
            found_group = None
            for existing_normalized, variants in groups.items():
                # Проверяем, является ли одно подстрокой другого
                if normalized in existing_normalized or existing_normalized in normalized:
                    # Берем более короткое название как ключ группы
                    if len(normalized) < len(existing_normalized):
                        # Перемещаем группу
                        groups[normalized] = groups.pop(existing_normalized)
                        found_group = normalized
                    else:
                        found_group = existing_normalized
                    break
            
            if found_group:
                groups[found_group].append(char)
                normalized_map[char] = found_group
            else:
                groups[normalized] = [char]
                normalized_map[char] = normalized
        
        return groups
    
    async def analyze_category_characteristics(
        self,
        session: AsyncSession,
        category_id: str,
        min_frequency: float = 0.3
    ) -> List[str]:
        """
        Анализирует характеристики СТЕ в категории и определяет значимые.
        
        Args:
            session: Сессия БД
            category_id: ID категории
            min_frequency: Минимальная частота (0-1) для значимой характеристики
            
        Returns:
            Список значимых характеристик
        """
        # Получаем все СТЕ категории
        stmt = select(STE).where(STE.category_id == category_id)
        result = await session.execute(stmt)
        stes = result.scalars().all()
        
        if not stes:
            return []
        
        # Собираем все характеристики
        all_characteristics = []
        stes_with_chars = 0
        for ste in stes:
            if ste.characteristics and isinstance(ste.characteristics, dict) and len(ste.characteristics) > 0:
                all_characteristics.append(ste.characteristics)
                stes_with_chars += 1
        
        # Если у большинства СТЕ нет характеристик, возвращаем пустой список
        # или используем альтернативные признаки (название, производитель)
        if not all_characteristics:
            return []
        
        # Если характеристики есть менее чем у 50% СТЕ, понижаем порог
        char_coverage = stes_with_chars / len(stes) if stes else 0
        if char_coverage < 0.5:
            # Используем более низкий порог для значимости
            min_frequency = max(0.1, min_frequency * char_coverage)
        
        # Подсчитываем частоту
        frequency = self.calculate_characteristic_frequency(all_characteristics)
        
        # Определяем порог (минимум 30% СТЕ должны иметь характеристику)
        threshold = max(1, int(len(all_characteristics) * min_frequency))
        
        # Фильтруем по частоте
        significant_chars = [
            char for char, freq in frequency.items()
            if freq >= threshold
        ]
        
        # Группируем похожие характеристики
        grouped = self.group_similar_characteristics(significant_chars)
        
        # Берем основной вариант из каждой группы (самый частый)
        final_characteristics = []
        for normalized, variants in grouped.items():
            # Находим самый частый вариант
            most_frequent = max(variants, key=lambda v: frequency.get(v, 0))
            final_characteristics.append(most_frequent)
        
        # Сортируем по частоте (по убыванию)
        final_characteristics.sort(key=lambda c: frequency.get(c, 0), reverse=True)
        
        return final_characteristics
    
    async def get_or_create_category_significant_characteristics(
        self,
        session: AsyncSession,
        category_id: str,
        category_name: str,
        min_frequency: float = 0.3
    ) -> List[str]:
        """
        Получает или создает список значимых характеристик для категории.
        
        Args:
            session: Сессия БД
            category_id: ID категории
            category_name: Название категории
            min_frequency: Минимальная частота
            
        Returns:
            Список значимых характеристик
        """
        # Проверяем, есть ли уже категория в БД
        stmt = select(Category).where(Category.category_id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if category and category.significant_characteristics:
            return category.significant_characteristics
        
        # Анализируем характеристики
        significant_chars = await self.analyze_category_characteristics(
            session, category_id, min_frequency
        )
        
        # Сохраняем в БД
        if category:
            category.significant_characteristics = significant_chars
        else:
            category = Category(
                category_id=category_id,
                name=category_name,
                significant_characteristics=significant_chars
            )
            session.add(category)
        
        await session.commit()
        
        return significant_chars

