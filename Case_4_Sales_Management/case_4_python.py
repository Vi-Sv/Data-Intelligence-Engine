# КЕЙС №4: СЕПАРАЦИЯ И СЕГМЕНТАЦИЯ КЛИЕНТСКОЙ БАЗЫ ПО VIP-ПОРОГУ ВЫРУЧКИ
# Реализация двухэтапного сита фильтрации (WHERE + HAVING) через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР
df = pd.read_sql("SELECT * FROM raw_orders", con=engine)

# 2. ПЕРВЫЙ ЭТАЖ: Жесткое отсечение неоплаченного мусора (Аналог WHERE)
df_paid = df[df['status'] == 'Paid'].copy()

# 3. НОРМАЛИЗАЦИЯ И ВАЛИДАЦИЯ ДАННЫХ
# .str.strip().str.lower() — срезаем невидимые пробелы и регистр (Аналог TRIM(LOWER))
df_paid['client_name'] = df_paid['client_name'].str.strip().str.lower()
# Заменяем пустые дыры NULL нулями (Аналог COALESCE)
df_paid['payment_amount'] = df_paid['payment_amount'].fillna(0)

# 4. ВТОРОЙ ЭТАЖ: Группировка и расчет суммарного оборота (Аналог GROUP BY + SUM)
client_revenue = df_paid.groupby('client_name')['payment_amount'].sum().reset_index()
client_revenue.columns = ['client_name', 'clean_sum']

# 5. ФИЛЬТРАЦИОННОЕ СИТО VIP-ПОРОГА (Аналог HAVING)
final_view = client_revenue[client_revenue['clean_sum'] > 500000]

# 6. СОРТИРОВКА ФИНАЛЬНОЙ ВИТРИНЫ
final_view = final_view.sort_values(by='clean_sum', ascending=False)
final_view.columns = ['Имя клиента', 'Общая сумма покупок']
