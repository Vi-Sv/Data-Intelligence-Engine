# КЕЙС №7: КОНТРОЛЬ ДЕФИЦИТА МАТЕРИАЛОВ И ФИЛЬТРАЦИЯ ПУСТЫХ СВЯЗЕЙ ПОСЛЕ МОСТА ДАННЫХ
# Реализация алгоритма Anti-Join для поиска абсолютного дефицита остатков через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ СПРАВОЧНИКОВ И РЕЕСТРОВ СКЛАДА
df_materials = pd.read_sql("SELECT * FROM raw_materials", con=engine)
df_stocks = pd.read_sql("SELECT * FROM warehouse_stocks", con=engine)

# 2. ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ НОМЕНКЛАТУРНОГО СПРАВОЧНИКА
df_materials['mat_name'] = df_materials['mat_name'].astype(str).str.strip().str.lower()

# 3. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ (Аналог LEFT JOIN)
# Сопрягаем справочник номенклатуры с остатками по ключу mat_code
merged_df = pd.merge(df_materials, df_stocks, on='mat_code', how='left')

# 4. ФИНИШНЫЙ ЭТАЖ ФИЛЬТРАЦИИ (Зеркало сеньорского WHERE ... OR ... IS NULL)
# Вычленяем позиции, у которых объем равен 0 или равен NaN (системный NULL из-за пустых связей)
final_view = merged_df[(merged_df['current_volume'] == 0) | (merged_df['current_volume'].isna())].copy()

# 5. ФИНАЛЬНАЯ ЗАЧИСТКА ВНЕШНИХ ПУСТОТ И ОФОРМЛЕНИЕ ВИТРИНЫ
# Заменяем образовавшиеся из-за отсутствия на складе связей NaN на жесткие нули
final_view['current_volume'] = final_view['current_volume'].fillna(0).astype(int)

# Выделяем целевые аналитические столбцы для отдела снабжения ПТО
final_view = final_view[['mat_name', 'current_volume']]
final_view.columns = ['Чистое имя дефицитного материала', 'Аргумент физически НЕТ']
