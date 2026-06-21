# КЕЙС №2: ЛОГИСТИЧЕСКОЕ СЖАТИЕ ДУБЛИКАТОВ И РАСЧЕТ СРЕДНИХ ОБЪЕМОВ ПОСТАВОК
# Реализация многоэтапной очистки и агрегации логистических логов через Pandas

import pandas as pd

# 1. ЗАГРУЗКА ИСТОЧНИКА
df = pd.read_sql("SELECT * FROM raw_shipments", con=engine)

# 2. ОЧИСТКА И УНИФИКАЦИЯ ТЕКСТОВЫХ ПОЛЕЙ
# .str.strip().str.lower() — полный аналог функций TRIM(LOWER()) в SQL
df['city'] = df['city'].str.strip().str.lower()
df['provider_name'] = df['provider_name'].str.strip().str.lower()

# Заменяем пустые дыры NULL нулями (аналог COALESCE)
df['volume'] = df['volume'].fillna(0)

# 3. ПЕРВЫЙ ЭТАЖ: Моментальное сжатие полных дубликатов по всей строке
# Метод .drop_duplicates() находит идентичные строки и оставляет только один уникальный экземпляр
df_clean = df.drop_duplicates()

# 4. ВТОРОЙ ЭТАЖ: Расчет среднего объема с группировкой по городам
# .groupby() — группировка (аналог GROUP BY), .mean() — расчет среднего (аналог AVG), .round(2) — округление
final_view = df_clean.groupby('city')['volume'].mean().round(2).reset_index()

# Переименовываем колонку для презентабельного вида на витрине
final_view.columns = ['Город поставки', 'Средний объем поставки']
