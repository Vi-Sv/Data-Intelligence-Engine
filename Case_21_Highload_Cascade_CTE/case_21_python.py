# КЕЙС №21: ВЛOЖЕННЫЕ CTE-МАГИСТРАЛИ И КAСКАДНАЯ ФИЛЬТРАЦИЯ ДАННЫХ
# Реализация каскадной последовательной фильтрации и многоуровневых CTE через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОЙ ТАБЛИЦЫ РАСХОДОВ
df = pd.read_sql("SELECT * FROM office_expenses", con=engine)

# 2. ПЕРВЫЙ ЭТАП ОБРАБОТКИ — ЦЕХ ОЧИСТКИ (Аналог WITH pure_data AS)
pure_df = df.copy()

# Удаляем концевые пробелы и приводим строковые поля к нижнему регистру
pure_df['office_city'] = pure_df['office_city'].astype(str).str.strip().str.lower()
pure_df['expense_item'] = pure_df['expense_item'].astype(str).str.strip().str.lower()

# Нейтрализуем системные пропуски NULL в объемах затрат числовыми нулями
pure_df['cost'] = pure_df['cost'].fillna(0).astype(int)

# Переименовываем столбцы для соответствия внутренней структуре цеха
pure_df.columns = ['expense_id', 'g1', 'g3', 'g2']

# 3. ВТOРОЙ ЭТАП ОБРАБОТКИ — КАСКАДНАЯ ФИЛЬТРАЦИЯ (Аналог каскада filtered_cities AS)
# Строго перехватываем очищенный массив данных из предыдущего этапа pure_df
filtered_df = pure_df[pure_df['g3'] == 'аренда'].copy()

# Выделяем целевые переменные каскада
filtered_df = filtered_df[['g1', 'g2', 'g3']]
filtered_df.columns = ['f1', 'f2', 'f3']

# 4. ГЛАВНЫЙ ВНЕШНИЙ КОНТУР И ИЗОЛЯЦИЯ АНОМАЛЬНОГО ВЕСА ЗАТРАТ (Аналог WHERE f2 > 150000)
final_view = filtered_df[filtered_df['f2'] > 150000].copy()

# Формируем и упорядочиваем финишную витрину по алфавиту городов (Аналог ORDER BY ASC)
final_view = final_view.sort_values(by='f1', ascending=True)
final_view = final_view[['f1', 'f2']]
final_view.columns = ['Города', 'Сумма аренды']
