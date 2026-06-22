# КЕЙС №3: АНАЛИЗ ТРАНЗАКЦИОННЫХ АНОМАЛИЙ И СРАВНИТЕЛЬНЫЙ АУДИТ ФИНТЕХ-ПОТОКА
# Реализация оконного конвейера расчетов без схлопывания строк через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР ДАННЫХ
df = pd.read_sql("SELECT * FROM raw_transactions", con=engine)

# Переводим строковые даты в полноценный формат времени для работы фильтров
df['date'] = pd.to_datetime(df['date'])

# 2. ЭЛЕГАНТНАЯ ФИЛЬТРАЦИЯ: Вырезаем месяц и год напрямую из временной метки (аналог EXTRACT)
df_filtered = df[(df['date'].dt.month == 5) & (df['date'].dt.year == 2026)].copy()

# 3. ВАЛИДАЦИЯ И ОЧИСТКА В ПОТОКЕ
# Убираем пустые ячейки NULL (.fillna(0)) и берем модуль числа (.abs())
df_filtered['clean_amount'] = df_filtered['amount'].fillna(0).abs()

# 4. ОКОННЫЙ КОНВЕЙЕР (Она самая "форсунка OVER()")
# Метод .transform('mean') вычисляет среднее по всей выборке и дублирует константу в каждую строчку
df_filtered['average_amount_period'] = df_filtered['clean_amount'].transform('mean').round(2)

# 5. ФОРМИРОВАНИЕ СОРТИРОВАННОЙ ВИТРИНЫ БИЗНЕСА
# Сортируем фрейм по убыванию очищенного объема (аналог ORDER BY DESC)
final_view = df_filtered.sort_values(by='clean_amount', ascending=False)

# Выделяем только целевые колонки отчета
final_view = final_view[['tx_id', 'user_id', 'clean_amount', 'average_amount_period']]
final_view.columns = ['ID транзакции', 'ID пользователя', 'Очищенный объем', 'Среднее значение за май']

