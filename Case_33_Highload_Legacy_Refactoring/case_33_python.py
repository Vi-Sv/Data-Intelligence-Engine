# КЕЙС №33: РЕФАКТОРИНГ ЛЕГАСИ-КОДА ЧЕРЕЗ CTE-МАГИСТРАЛИ И ПЛОСКИЙ PIVOT-АГРЕГАТ
# Реализация оптимизации легаси-запроса, условной Pivot-агрегации и LEFT JOIN через Pandas

import pandas as pd
import numpy as np

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ДАННЫХ ИЗ РЕЕСТРОВ ПОЛЬЗОВАТЕЛЕЙ И ЗАКАЗОВ
df_users = pd.read_sql("SELECT * FROM users", con=engine)
df_orders = pd.read_sql("SELECT * FROM orders", con=engine)

# 2. ПЕРВЫЙ ЭТАП ОБРАБОТКИ — ВЫЧИСЛИТЕЛЬНЫЙ ЦЕХ АГРЕГАЦИИ (Аналог подзапроса select_sum)
# Проводим тотальную чистку качества данных (Data Quality) на транзакционном логе заказов
orders_clean = df_orders.copy()
orders_clean['cat'] = orders_clean['cat'].astype(str).str.strip().str.lower()
orders_clean['amount'] = orders_clean['amount'].fillna(0).astype(int)

# Внедряем логические стрелочные переключатели категорий на лету (Зеркало CASE WHEN)
orders_clean['it_amount'] = np.where(orders_clean['cat'] == 'it', orders_clean['amount'], 0)
orders_clean['auto_amount'] = np.where(orders_clean['cat'] == 'auto', orders_clean['amount'], 0)

# Сжимаем лог до уникальных пользователей с расчетом условных сумм (Аналог GROUP BY)
orders_pivot = orders_clean.groupby('users_id').agg({
    'it_amount': 'sum',
    'auto_amount': 'sum'
}).reset_index()
orders_pivot.columns = ['g1', 'g2', 'g3']

# 3. ВТОРОЙ ЭТАП ОБРАБОТКИ — НОРМАЛИЗАЦИЯ И ФИЛЬТРАЦИЯ СПРАВОЧНИКА ПОЛЬЗОВАТЕЛЕЙ
users_clean = df_users.copy()
# [Исправление ТЗ джуна] Вырезаем на входе исключительно активный статус клиентов
users_filtered = users_clean[users_clean['status'] == 'active'].copy()
users_filtered['user_name'] = users_filtered['user_name'].astype(str).str.strip()

# 4. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ ДЛЯ ФОРМИРОВАНИЯ ВИТРИНЫ (Аналог LEFT JOIN)
# Сшиваем отфильтрованных пользователей со сжатой матрицей сумм по ключу идентификатора
final_merged = pd.merge(users_filtered, orders_pivot, left_on='users_id', right_on='g1', how='left')

# 5. ФИНАЛЬНАЯ ЗАЧИСТКА ВНЕШНИХ ПУСТОТ И СОРТИРОВКА ВИТРИНЫ
# Заменяем образовавшиеся из-за пустых связей NaN для пользователей без заказов на жесткие нули
final_merge['g2'] = final_merge['g2'].fillna(0).astype(int)
final_merge['g3'] = final_merge['g3'].fillna(0).astype(int)

# Формируем и упорядочиваем финишный результат по алфавиту (Аналог ORDER BY ASC)
final_view = final_merge.sort_values(by='user_name', ascending=True)
final_view = final_view[['user_name', 'g2', 'g3']]
final_view.columns = ['Имена пользователей', 'IT', 'AUTO']
