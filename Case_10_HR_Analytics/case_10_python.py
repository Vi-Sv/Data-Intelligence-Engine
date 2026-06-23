# КЕЙС №10: БАЗОВОЕ ОКНО АГРЕГАЦИИ И СЕПАРАЦИЯ ФИЛИАЛОВ ХОЛДИНГА
# Реализация оконного секционирования (PARTITION BY) через аналитический вектор Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ЗАРПЛАТНОЙ ТАБЛИЦЫ
df = pd.read_sql("SELECT * FROM raw_salaries", con=engine)

# 2. НОРМАЛИЗАЦИЯ И ТЕКСТОВАЯ СТАНДАРТИЗАЦИЯ ДАННЫХ
# Удаляем скрытые концевые пробелы и приводим строки к нижнему регистру
df['branch_name'] = df['branch_name'].astype(str).str.strip().str.lower()
df['department'] = df['department'].astype(str).str.strip().str.lower()

# 3. ВАЛИДАЦИЯ ФИНАНСОВЫХ МЕТРИК
# Заменяем пропуски NULL (NaN) в окладах жесткими нулями
df['salary'] = df['salary'].fillna(0).astype(int)

# 4. ОКОННЫЙ КОНВЕЙЕР СЕКЦИОНИРОВАНИЯ (Аналог AVG() OVER(PARTITION BY))
# Группируем датафрейм по городам филиалов через .groupby('branch_name')
# Инструмент .transform('mean') рассчитывает среднее внутри группы и распределяет его по детальным строкам
df['branch_average_salary'] = df.groupby('branch_name')['salary'].transform('mean').round(2)

# 5. СОРТИРОВКА И ФОРМИРОВАНИЕ ФИНАЛЬНОЙ ВИТРИНЫ
# Сортируем данные по алфавитному порядку филиалов (Аналог ORDER BY ASC)
final_view = df.sort_values(by='branch_name', ascending=True)

# Изолируем целевые аналитические столбцы отчета
final_view = final_view[['emp_id', 'branch_name', 'department', 'salary', 'branch_average_salary']]
final_view.columns = ['ID сотрудника', 'Город филиала', 'Департамент', 'Чистый оклад', 'Средний оклад филиала']
