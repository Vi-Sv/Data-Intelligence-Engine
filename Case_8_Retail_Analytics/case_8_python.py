# КЕЙС №8: СОРТИРОВОЧНЫЙ ЧИТ-КОД NULLS LAST И ЗАЩИТА КАТАЛОГА В РИТЕЙЛЕ
# Реализация предварительной агрегации, левостороннего объединения и сортировки через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ ТАБЛИЦ
df_products = pd.read_sql("SELECT * FROM products", con=engine)
df_sales_logs = pd.read_sql("SELECT * FROM sales_logs", con=engine)

# 2. ПРЕДВАРИТЕЛЬНАЯ АГРЕГАЦИЯ И ВАЛИДАЦИЯ ЛОГОВ ПРОДАЖ (Аналог подзапроса t2)
# Локализуем системные пропуски NULL нулями перед математическим суммированием
df_sales_logs['quantity'] = df_sales_logs['quantity'].fillna(0).astype(int)

# Сжимаем транзакционный лог до уникальных ID товаров, ликвидируя дубликаты продаж
sales_agg = df_sales_logs.groupby('item_id')['quantity'].sum().reset_index()
sales_agg.columns = ['item_id', 'total_quantity']

# 3. НОРМАЛИЗАЦИЯ СПРАВОЧНИКА ТОВАРОВ
df_products['item_name'] = df_products['item_name'].astype(str).str.strip().str.lower()

# 4. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ (Аналог LEFT JOIN)
# Параметр how='left' оставляет каталог товаров неприкасаемым, сохраняя позиции без продаж
merged_df = pd.merge(df_products, sales_agg, on='item_id', how='left')

# 5. ФИНАЛЬНАЯ ЗАЧИСТКА ВНЕШНИХ ПУСТОТ И СОРТИРОВКА ВИТРИНЫ
# Заменяем образовавшиеся из-за пустых связей NaN на жесткие нули
merged_df['total_quantity'] = merged_df['total_quantity'].fillna(0).astype(int)

# Сортируем датафрейм по убыванию объемов продаж (Аналог ORDER BY DESC)
final_view = merged_df.sort_values(by='total_quantity', ascending=False)

# Выделяем целевые аналитические колонки
final_view = final_view[['item_name', 'total_quantity']]
final_view.columns = ['Список товаров', 'Количество проданных штук']
