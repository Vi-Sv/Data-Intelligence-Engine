# КЕЙС №13: РАСЧЕТ НАКОПИТЕЛЬНОГО ИТОГА (RUNNING TOTAL) ДЛЯ МОНИТОРИНГА КАССОВЫХ РАЗРЫВОВ
# Реализация кумулятивной суммы (нарастающего итога) временного ряда через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА РЕЕСТРА ПРОДАЖ
df = pd.read_sql("SELECT * FROM shop_sales", con=engine)

# 2. ВАЛИДАЦИЯ И ПРИВЕДЕНИЕ ТИПОВ ВРЕМЕННОГО РЯДА
df['sale_date'] = pd.to_datetime(df['sale_date'])

# 3. ПРЕДВАРИТЕЛЬНАЯ КРИТИЧЕСКАЯ СОРТИРОВКА ПОТОКА
# Упорядочиваем датафрейм по дате и ID чека для обеспечения уникальности шага кумулятивного расчета
df = df.sort_values(by=['sale_date', 'sale_id'], ascending=[True, True]).copy()

# 4. ВАЛИДАЦИЯ ФИНАНСОВЫХ МЕТРИК
df['revenue'] = df['revenue'].fillna(0).astype(int)

# 5. КОНВЕЙЕР НАРАСТАЮЩЕГО ИТОГА (Аналог SUM() OVER(ORDER BY))
# Метод .cumsum() выполняет последовательное кумулятивное сложение элементов сверху вниз по всему датафрейму
df['running_total_revenue'] = df['revenue'].cumsum()

# 6. ФОРМИРОВАНИЕ И ОФОРМЛЕНИЕ ФИНАЛЬНОЙ ВИТРИНЫ БИЗНЕСА
final_view = df[['sale_date', 'revenue', 'running_total_revenue']]
final_view.columns = ['Даты продаж', 'Выручка', 'Динамика (Накопительный итог)']
