"""
Парсер Excel файла с данными о СТЕ
Обрабатывает множественные листы, разные форматы характеристик и орфографические ошибки
"""
import pandas as pd
from typing import List, Dict, Any, Optional
import re
from pathlib import Path
import unicodedata


class ExcelParser:
    """Парсер Excel файла с СТЕ"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализует текст для обработки орфографических ошибок.
        Убирает лишние пробелы, приводит к единому формату.
        
        Args:
            text: Исходный текст
            
        Returns:
            Нормализованный текст
        """
        if not text:
            return ""
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', str(text).strip())
        
        # Нормализуем кавычки
        text = text.replace('«', '"').replace('»', '"')
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Убираем нулевые символы
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char == '\n' or char == '\t')
        
        return text.strip()
    
    @staticmethod
    def normalize_key(key: str) -> str:
        """
        Нормализует ключ характеристики для группировки похожих.
        Обрабатывает орфографические ошибки и вариации написания.
        
        Args:
            key: Исходный ключ
            
        Returns:
            Нормализованный ключ
        """
        if not key:
            return ""
        
        # Приводим к нижнему регистру для сравнения
        normalized = key.lower().strip()
        
        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Нормализуем знаки препинания
        normalized = normalized.replace(':', '').replace(';', '').replace(',', '')
        normalized = normalized.rstrip('.,;:!?')
        
        # Общие замены для обработки ошибок
        replacements = {
            'характеристика': '',
            'параметр': '',
            'свойство': '',
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()
    
    @staticmethod
    def parse_characteristics(raw_characteristics: str) -> Dict[str, Any]:
        """
        Парсит строку характеристик в словарь.
        Поддерживает различные форматы:
        - "Ключ1:Значение1;Ключ2:Значение2;..."
        - "Ключ1: Значение1 ;Ключ2: Значение2 ;..."
        - "Ключ1:Значение1, Ключ2:Значение2, ..."
        
        Args:
            raw_characteristics: Сырая строка характеристик
            
        Returns:
            Словарь характеристик
        """
        if not raw_characteristics or pd.isna(raw_characteristics):
            return {}
        
        characteristics = {}
        
        # Нормализуем текст
        text = ExcelParser.normalize_text(str(raw_characteristics))
        
        if not text:
            return {}
        
        # Пробуем разные разделители - сначала точка с запятой, затем запятая
        # Используем регулярное выражение для более гибкого парсинга
        # Паттерн: ключ (может содержать пробелы и двоеточие) : значение до точки с запятой или конца строки
        pattern = r'([^:]+?):\s*([^;]+?)(?:;|$)'
        matches = re.findall(pattern, text)
        
        for key, value in matches:
            key = ExcelParser.normalize_text(key)
            value = ExcelParser.normalize_text(value)
            
            if key and value:
                # Сохраняем оригинальный ключ для читаемости, но используем нормализованный для группировки
                characteristics[key] = value
        
        # Если не нашлось совпадений, пробуем более простой парсинг
        if not characteristics:
            # Разбиваем по точке с запятой или запятой (если они с пробелами после)
            parts = re.split(r'[;]\s*', text)
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                # Ищем разделитель ":"
                if ':' in part:
                    # Разбиваем по первому вхождению ":"
                    key_value = part.split(':', 1)
                    if len(key_value) == 2:
                        key = ExcelParser.normalize_text(key_value[0])
                        value = ExcelParser.normalize_text(key_value[1])
                        
                        if key and value:
                            characteristics[key] = value
        
        return characteristics
    
    @staticmethod
    def clean_value(value: Any) -> Optional[str]:
        """
        Очищает значение от NULL, NaN и нормализует.
        
        Args:
            value: Значение для очистки
            
        Returns:
            Очищенное значение или None
        """
        if pd.isna(value) or value is None:
            return None
        
        value_str = str(value).strip()
        
        # Проверяем на NULL в разных форматах
        if not value_str or value_str.lower() in ['null', 'none', 'nan', '']:
            return None
        
        # Нормализуем текст
        value_str = ExcelParser.normalize_text(value_str)
        
        return value_str if value_str else None
    
    def parse_excel_sheet(self, df: pd.DataFrame, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Парсит один лист Excel файла.
        
        Args:
            df: DataFrame с данными листа
            sheet_name: Название листа (для логирования)
            
        Returns:
            Список словарей с данными о СТЕ
        """
        ste_list = []
        
        # Нормализуем названия колонок (убираем пробелы, приводим к нижнему регистру для сравнения)
        df.columns = df.columns.str.strip()
        
        # Определяем маппинг колонок (на случай разных названий и орфографических ошибок)
        column_mapping = {}
        
        # Ищем колонки по различным вариантам названий
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # ID СТЕ
            if 'id сте' in col_lower or 'id_сте' in col_lower or col_lower == 'сте_id':
                column_mapping[col] = 'ste_id'
            # Название СТЕ
            elif 'название сте' in col_lower or 'название_сте' in col_lower:
                column_mapping[col] = 'name'
            # Ссылка на картинку
            elif 'ссылка' in col_lower and ('картинк' in col_lower or 'изображен' in col_lower):
                column_mapping[col] = 'image_url'
            # Модель
            elif col_lower == 'модель' or col_lower == 'model':
                column_mapping[col] = 'model'
            # Страна происхождения
            elif 'страна' in col_lower and 'происхожд' in col_lower:
                column_mapping[col] = 'country'
            # Производитель
            elif col_lower == 'производитель' or 'manufacturer' in col_lower:
                column_mapping[col] = 'manufacturer'
            # ID категории
            elif 'id категори' in col_lower or 'id_категори' in col_lower:
                column_mapping[col] = 'category_id'
            # Название категории
            elif 'название категори' in col_lower or 'название_категори' in col_lower:
                column_mapping[col] = 'category_name'
            # Характеристики
            elif col_lower == 'характеристики' or 'characteristics' in col_lower:
                column_mapping[col] = 'characteristics_raw'
        
        # Переименовываем колонки
        df = df.rename(columns=column_mapping)
        
        # Парсим данные
        for index, row in df.iterrows():
            try:
                # Получаем данные строки с обработкой разных вариантов названий колонок
                ste_data = {
                    'ste_id': None,
                    'name': None,
                    'image_url': None,
                    'model': None,
                    'country': None,
                    'manufacturer': None,
                    'category_id': None,
                    'category_name': None,
                    'characteristics_raw': None,
                }
                
                # Заполняем данные из доступных колонок
                for key in ste_data.keys():
                    if key in df.columns:
                        value = row.get(key)
                        if key == 'ste_id' or key == 'category_id':
                            # ID должны быть строками
                            cleaned = self.clean_value(value)
                            ste_data[key] = str(cleaned) if cleaned else None
                        else:
                            ste_data[key] = self.clean_value(value)
                
                # Пропускаем строки без обязательных полей
                if not ste_data['ste_id'] or not ste_data['name']:
                    continue
                
                # Парсим характеристики (даже если они пустые или отсутствуют)
                raw_char = ste_data.get('characteristics_raw', '') or ''
                ste_data['characteristics'] = self.parse_characteristics(raw_char)
                
                ste_list.append(ste_data)
                
            except Exception as e:
                # Логируем ошибки, но продолжаем обработку
                sheet_info = f" (лист: {sheet_name})" if sheet_name else ""
                print(f"Ошибка при парсинге строки {index}{sheet_info}: {e}")
                continue
        
        return ste_list
    
    def parse_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Парсит Excel файл (все листы) и возвращает список СТЕ.
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            Список словарей с данными о СТЕ
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        all_ste_list = []
        
        # Читаем все листы Excel файла
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = excel_file.sheet_names
        
        print(f"Найдено листов в файле: {len(sheet_names)}")
        
        for sheet_name in sheet_names:
            try:
                print(f"Обработка листа: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
                
                # Пропускаем пустые листы
                if df.empty:
                    print(f"  Лист '{sheet_name}' пуст, пропускаем")
                    continue
                
                # Парсим лист
                ste_list = self.parse_excel_sheet(df, sheet_name)
                print(f"  Обработано СТЕ из листа '{sheet_name}': {len(ste_list)}")
                
                all_ste_list.extend(ste_list)
                
            except Exception as e:
                print(f"Ошибка при обработке листа '{sheet_name}': {e}")
                continue
        
        print(f"Всего обработано СТЕ: {len(all_ste_list)}")
        
        return all_ste_list


def parse_ste_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Удобная функция для парсинга файла СТЕ.
    Обрабатывает все листы Excel файла.
    
    Args:
        file_path: Путь к Excel файлу
        
    Returns:
        Список словарей с данными о СТЕ
    """
    parser = ExcelParser()
    return parser.parse_excel(file_path)
