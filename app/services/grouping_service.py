"""
Сервис группировки СТЕ по значимым характеристикам
"""
from typing import List, Dict, Any, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.database import STE, Aggregation, AggregationItem
from app.services.characteristic_analyzer import CharacteristicAnalyzer
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import defaultdict


class GroupingService:
    """Сервис для группировки СТЕ"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.characteristic_analyzer = CharacteristicAnalyzer()
        # Инициализируем модель для вычисления схожести (легковесная)
        self.embedding_model = None
    
    def _get_embedding_model(self):
        """Ленивая загрузка модели embeddings"""
        if self.embedding_model is None:
            from app.config import settings
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self.embedding_model
    
    def _extract_grouping_key(self, ste: STE, significant_chars: List[str]) -> str:
        """
        Извлекает ключ группировки для СТЕ на основе значимых характеристик.
        Если характеристик нет или их мало, использует альтернативные признаки.
        
        Args:
            ste: СТЕ
            significant_chars: Список значимых характеристик
            
        Returns:
            Строка-ключ для группировки
        """
        key_parts = []
        
        # Сначала пытаемся использовать характеристики
        if ste.characteristics and isinstance(ste.characteristics, dict):
            for char in significant_chars:
                if char in ste.characteristics:
                    value = ste.characteristics[char]
                    if value:  # Проверяем, что значение не пустое
                        key_parts.append(f"{char}={value}")
        
        # Если характеристик мало или нет, используем альтернативные признаки
        if len(key_parts) < 2:
            # Используем производителя и модель как дополнительный признак
            if ste.manufacturer:
                key_parts.append(f"manufacturer={ste.manufacturer}")
            if ste.model:
                key_parts.append(f"model={ste.model}")
            
            # Если все еще мало признаков, используем часть названия
            if len(key_parts) < 2 and ste.name:
                # Берем первые слова названия (до 3 слов)
                name_words = ste.name.split()[:3]
                if name_words:
                    key_parts.append(f"name_prefix={' '.join(name_words)}")
        
        return ";".join(sorted(key_parts)) if key_parts else "no_characteristics"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Вычисляет схожесть между двумя текстами.
        
        Args:
            text1: Первый текст
            text2: Второй текст
            
        Returns:
            Коэффициент схожести от 0 до 1
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            model = self._get_embedding_model()
            embeddings = model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(max(0.0, min(1.0, similarity)))
        except Exception:
            # В случае ошибки возвращаем простую схожесть по словам
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0
    
    def _group_by_exact_match(
        self,
        stes: List[STE],
        significant_chars: List[str]
    ) -> Dict[str, List[STE]]:
        """
        Группирует СТЕ по точному совпадению значений значимых характеристик.
        
        Args:
            stes: Список СТЕ
            significant_chars: Значимые характеристики
            
        Returns:
            Словарь {ключ_группы: [СТЕ]}
        """
        groups = defaultdict(list)
        
        for ste in stes:
            key = self._extract_grouping_key(ste, significant_chars)
            groups[key].append(ste)
        
        return dict(groups)
    
    def _merge_similar_groups(
        self,
        groups: Dict[str, List[STE]],
        similarity_threshold: float = 0.7
    ) -> Dict[str, List[STE]]:
        """
        Объединяет похожие группы на основе схожести названий СТЕ.
        
        Args:
            groups: Словарь групп
            similarity_threshold: Порог схожести
            
        Returns:
            Объединенные группы
        """
        if not groups:
            return {}
        
        group_keys = list(groups.keys())
        merged = {}
        used_keys = set()
        
        for i, key1 in enumerate(group_keys):
            if key1 in used_keys:
                continue
            
            merged_group = groups[key1].copy()
            
            # Ищем похожие группы
            for j, key2 in enumerate(group_keys):
                if i >= j or key2 in used_keys:
                    continue
                
                # Проверяем схожесть по среднему названию СТЕ в группах
                names1 = [ste.name for ste in groups[key1]]
                names2 = [ste.name for ste in groups[key2]]
                
                avg_name1 = " ".join(names1[:3])  # Берем первые 3 для скорости
                avg_name2 = " ".join(names2[:3])
                
                similarity = self._calculate_similarity(avg_name1, avg_name2)
                
                if similarity >= similarity_threshold:
                    merged_group.extend(groups[key2])
                    used_keys.add(key2)
            
            if merged_group:
                merged[key1] = merged_group
                used_keys.add(key1)
        
        return merged
    
    async def group_stes(
        self,
        session: AsyncSession,
        category_id: str = None,
        ste_ids: List[int] = None,
        similarity_threshold: float = 0.7,
        min_group_size: int = 2,
        max_group_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Группирует СТЕ по значимым характеристикам.
        
        Args:
            session: Сессия БД
            category_id: ID категории (если указан - фильтр)
            ste_ids: Список ID СТЕ для группировки (если None - все)
            similarity_threshold: Порог схожести
            min_group_size: Минимальный размер группы
            max_group_size: Максимальный размер группы
            
        Returns:
            Список групп СТЕ
        """
        # Получаем СТЕ
        stmt = select(STE)
        
        if category_id:
            stmt = stmt.where(STE.category_id == category_id)
        
        if ste_ids:
            stmt = stmt.where(STE.id.in_(ste_ids))
        
        result = await session.execute(stmt)
        stes = result.scalars().all()
        
        if not stes:
            return []
        
        # Группируем по категориям
        categories = {}
        for ste in stes:
            cat_id = ste.category_id or "unknown"
            if cat_id not in categories:
                categories[cat_id] = []
            categories[cat_id].append(ste)
        
        all_groups = []
        
        # Для каждой категории
        for cat_id, cat_stes in categories.items():
            # Получаем значимые характеристики
            if cat_id != "unknown" and cat_stes:
                cat_name = cat_stes[0].category_name or "Неизвестная категория"
                significant_chars = await self.characteristic_analyzer.get_or_create_category_significant_characteristics(
                    session, cat_id, cat_name
                )
            else:
                significant_chars = []
            
            # Группируем по точному совпадению
            exact_groups = self._group_by_exact_match(cat_stes, significant_chars)
            
            # Объединяем похожие группы
            merged_groups = self._merge_similar_groups(exact_groups, similarity_threshold)
            
            # Фильтруем по размеру групп
            for key, group_stes in merged_groups.items():
                if min_group_size <= len(group_stes) <= max_group_size:
                    # Формируем характеристики группировки
                    grouping_chars = {}
                    if group_stes:
                        # Берем общие характеристики или альтернативные признаки
                        first_ste = group_stes[0]
                        if first_ste.characteristics and isinstance(first_ste.characteristics, dict):
                            # Используем характеристики, если они есть
                            for char in significant_chars:
                                if char in first_ste.characteristics:
                                    grouping_chars[char] = first_ste.characteristics[char]
                        else:
                            # Если характеристик нет, используем альтернативные признаки
                            if first_ste.manufacturer:
                                grouping_chars["производитель"] = first_ste.manufacturer
                            if first_ste.model:
                                grouping_chars["модель"] = first_ste.model
                            if first_ste.name:
                                # Берем первые слова названия
                                name_words = first_ste.name.split()[:3]
                                if name_words:
                                    grouping_chars["название_префикс"] = " ".join(name_words)
                    
                    all_groups.append({
                        "category_id": cat_id,
                        "category_name": cat_stes[0].category_name if cat_stes else None,
                        "grouping_key": key,
                        "grouping_characteristics": grouping_chars,
                        "stes": group_stes,
                        "size": len(group_stes)
                    })
        
        return all_groups
    
    async def create_aggregation_from_group(
        self,
        session: AsyncSession,
        group_data: Dict[str, Any],
        status: str = "auto"
    ) -> Aggregation:
        """
        Создает агрегацию из группы СТЕ.
        
        Args:
            session: Сессия БД
            group_data: Данные группы
            status: Статус агрегации (auto/manual)
            
        Returns:
            Созданная агрегация
        """
        # Формируем название агрегации
        name_parts = []
        if group_data.get("category_name"):
            name_parts.append(group_data["category_name"])
        
        grouping_chars = group_data.get("grouping_characteristics", {})
        if grouping_chars:
            char_str = ", ".join([f"{k}: {v}" for k, v in list(grouping_chars.items())[:2]])
            name_parts.append(char_str)
        
        name = " | ".join(name_parts) if name_parts else f"Группа из {group_data['size']} СТЕ"
        
        # Создаем агрегацию
        aggregation = Aggregation(
            name=name,
            category_id=group_data.get("category_id"),
            grouping_characteristics=grouping_chars,
            status=status
        )
        session.add(aggregation)
        await session.flush()
        
        # Добавляем СТЕ в агрегацию
        for idx, ste in enumerate(group_data["stes"]):
            item = AggregationItem(
                aggregation_id=aggregation.id,
                ste_id=ste.id,
                order=idx
            )
            session.add(item)
        
        await session.commit()
        await session.refresh(aggregation)
        
        return aggregation

