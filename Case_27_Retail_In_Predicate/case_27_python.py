# КЕЙС №27: МНОЖЕСТВЕННЫЕ ПОДЗАПРОСЫ И СИТО ПРЕДИКАТОВ IN В РИТЕЙЛ-МАРКЕТИНГЕ
# Реализация предикативной фильтрации множеств (Оператор IN) через методы Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОГО МАССИВА ДОХОДОВ ФИЛИАЛОВ
df = pd.read_sql("SELECT * FROM branch_revenues", con=engine)

# 2. ПРЕДВАРИТЕЛЬНАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ (Data Quality)
df_clean = df.copy()
df_clean['city_name'] = df_clean['city_name'].astype(str).str.strip().str.lower()
df_clean['region_zone'] = df_clean['region_zone'].astype(str).str.strip().str.lower()
df_clean['monthly_profit'] = df_clean['monthly_profit'].fillna(0).astype(int)

# 3. ВЫЧИСЛИТЕЛЬНЫЙ ЦЕХ CTE-ОТБОРА (Аналог конструкции WITH top_profit_subquery AS)
# Фильтруем целевую южную зону и отсекаем по установленному порогу прибыли
subquery_df = df_clean[
    (df_clean['monthly_profit'] > 250000) & 
    (df_clean['region_zone'] == 'юг')
].copy()

# Метод .unique() намертво сжимает массив до уникальных городов, избавляя память от дубликатов строк (Аналог DISTINCT)
target_cities = subquery_df['city_name'].unique()

# 4. ГЛАВНЫЙ КОНТУР ФИЛЬТРАЦИИ И ВЫВОД НА ВИТРИНУ (Аналог WHERE IN)
# Метод .isin() работает как динамический внутренний фильтр, оставляя только города из белого списка
final_view = df_clean[df_clean['city_name'].isin(target_cities)].copy()

# Сортируем готовую витрину по убыванию финансовой прибыли (Аналог ORDER BY 2 DESC)
final_view = final_view.sort_values(by='monthly_profit', ascending=False)
final_view = final_view[['city_name', 'monthly_profit']]
final_view.columns = ['Зачищенный город', 'Прибыль']
