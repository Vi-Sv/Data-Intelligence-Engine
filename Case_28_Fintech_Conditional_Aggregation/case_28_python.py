# КЕЙС №28: ЛOГИЧЕСКOЕ ВEТВЛEНИЕ CASE WHEN ВНУТРИ АГРEГAЦИИ ДЛЯ СБОРКИ PIVOT-ВИТРИНЫ
# Реализация условной агрегации и развертывания PIVOT-структур через методы Pandas

import pandas as pd
import numpy as np

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОГО ЛОГА ТОРГОВЫХ ТРАНЗАКЦИЙ
df = pd.read_sql("SELECT * FROM store_transactions", con=engine)

# 2. ПЕРВИЧНАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ (Data Quality)
df_clean = df.copy()
df_clean['manager_name'] = df_clean['manager_name'].astype(str).str.strip().str.lower()
df_clean['item_category'] = df_clean['item_category'].astype(str).str.strip().str.lower()
df_clean['amount'] = df_clean['amount'].fillna(0).astype(int)

# 3. ФИЛЬТРАЦИЯ НА ВХОДЕ (Аналог блока WHERE NOT LIKE)
df_filtered = df_clean[~df_clean['manager_name'].str.contains('тест', na=False)].copy()

# 4. ВНЕДРЕНИЕ СТРЕЛОЧНЫХ ПЕРЕКЛЮЧАТЕЛЕЙ ДЛЯ КАТЕГОРИЙ (Аналог CASE WHEN)
# При помощи np.where создаем изолированные векторы сумм для целевых категорий ритейла
# [Исправление] Строгие маски сравнения заданы в нижнем регистре ('электроника', 'одежда')
df_filtered['elec_amount'] = np.where(df_filtered['item_category'] == 'электроника', df_filtered['amount'], 0)
df_filtered['cloth_amount'] = np.where(df_filtered['item_category'] == 'одежда', df_filtered['amount'], 0)

# 5. МАКРО-ГРУППИРОВКА И УСЛОВНАЯ АГРЕГАЦИЯ (Аналог GROUP BY + SUM)
# Схлопываем данные по менеджерам с одновременным суммированием базовых и расчетных полей
pivot_view = df_filtered.groupby('manager_name').agg({
    'amount': 'sum',
    'elec_amount': 'sum',
    'cloth_amount': 'sum'
}).reset_index()

# 6. СОРТИРОВКА И ОФОРМЛЕНИЕ ФИНАЛЬНОЙ ПРOДУКТОВОЙ ВИТРИНЫ
final_view = pivot_view.sort_values(by='amount', ascending=False)
final_view.columns = ['Менеджер', 'Общая сумма всех продаж менеджера', 'Сумма продаж электроники', 'Сумма продаж одежды']
