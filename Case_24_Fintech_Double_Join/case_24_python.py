# КЕЙС №24: СТЕ-МАГИСТРАЛИ И СКВОЗНАЯ СШИВКА ДВОЙНОГО LEFT JOIN ДЛЯ СВЕРКИ БАЛАНСОВ
# Реализация последовательного левостороннего объединения нескольких источников и фильтрации равенства через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ ТАБЛИЦ ФИНТЕХА
df_clients = pd.read_sql("SELECT * FROM clients", con=engine)
df_payments = pd.read_sql("SELECT * FROM client_payments", con=engine)
df_bonuses = pd.read_sql("SELECT * FROM client_bonuses", con=engine)

# 2. ПРЕДВАРИТЕЛЬНАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ (Data Quality)
df_clients['client_name'] = df_clients['client_name'].astype(str).str.strip().str.lower()

# 3. ПОСЛЕДОВАТЕЛЬНОЕ РАЗВЕРТЫВАНИЕ МОСТОВ ДАННЫХ (Аналог двойного LEFT JOIN в CTE)
# Шаг А: Объединяем справочник клиентов с логом оплат по ключу client_id
merge_1 = pd.merge(df_clients, df_payments, on='client_id', how='left')

# Шаг Б: Пришиваем лог бонусов строго к полученному массиву по базовому ключу client_id
# Это сохраняет в контуре "молчунов", у которых отсутствовали транзакции в одной из таблиц
final_merge = pd.merge(merge_1, df_bonuses, on='client_id', how='left')

# 4. ЗАЧИСТКА ВНЕШНИХ ПУСТОТ И КАНАЛИЗАЦИЯ МЕТРИК
# Нейтрализуем образовавшиеся из-за пустых связей NaN в числовые нули 0 (Аналог COALESCE)
final_merge['pay_amount'] = final_merge['pay_amount'].fillna(0).astype(int)
final_merge['bonus_amount'] = final_merge['bonus_amount'].fillna(0).astype(int)

# 5. ХИРУРГИЧЕСКОЕ СИТО ВЗАИМОРАСЧЕТОВ (Аналог WHERE g3 = g4)
# Вырезаем только те строки, где сумма платежа абсолютно эквивалентна объему бонусов
final_view = final_merge[final_merge['pay_amount'] == final_merge['bonus_amount']].copy()

# 6. ФОРМИРОВАНИЕ СТЕРИЛЬНОЙ ИТОГОВОЙ ВИТРИНЫ
final_view = final_view.sort_values(by='client_name', ascending=True)
final_view = final_view[['client_name']]
final_view.columns = ['Клиенты чей платеж равен сумме бонусов']
