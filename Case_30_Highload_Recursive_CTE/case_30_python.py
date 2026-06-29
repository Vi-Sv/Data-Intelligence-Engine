# КЕЙС №23: МНОГОСТУПЕНЧАТЫЕ РЕКУРСИВНЫЕ CTE И ПОСТРОЕНИЕ ГРАФОВЫХ ИЕРАРХИЙ ШТАТА
# СТАТУС: ТЕХНИЧЕСКАЯ ДОКУМЕНТАЦИЯ ПОВЫШЕННОЙ СЛОЖНОСТИ (R&D-ПOЛИГOН)
# Реализация алгоритма обхода графа зависимостей и расчета уровней вложенности через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОЙ ИЕРАРХИЧЕСКОЙ СТРУКТУРЫ ХОЛДИНГА
df = pd.read_sql("SELECT * FROM company_structure", con=engine)

# 2. ПЕРВИЧНАЯ НОРМАЛИЗАЦИЯ КАЧЕСТВА ДАННЫХ (Data Quality)
df_clean = df.copy()
df_clean['emp_name'] = df_clean['emp_name'].astype(str).str.strip().str.lower()

# Примечание: В промышленной разработке обработка рекурсивных графов на больших объемах 
# эффективнее и стабильнее реализуется на уровне Python, а не через синтаксис SQL WITH RECURSIVE.

# 3. ИНИЦИАЛИЗАЦИЯ ИЕРАРХИЧЕСКОГО СЛОВАРЯ ДЛЯ ПОСТРОЕНИЯ ДЕРЕВА
# Создаем карту сопоставления сотрудника и его непосредственного руководителя
manager_map = dict(zip(df_clean['emp_id'], df_clean['manager_id']))

# 4. ФУНКЦИЯ ИТЕРАЦИОННОГО ВЫЧИСЛЕНИЯ ГЛУБИНЫ УЗЛА ГРАФА
def get_hierarchy_level(emp_id, mapping, cache):
    if emp_id not in mapping or pd.isna(mapping[emp_id]):
        return 1 # Базовый уровень (Генеральный директор / верхний узел)
    if emp_id in cache:
        return cache[emp_id] # Извлечение из кэша для оптимизации скорости
    
    # Рекурсивный спуск вверх до корневого элемента
    parent_id = mapping[emp_id]
    level = 1 + get_hierarchy_level(parent_id, mapping, cache)
    cache[emp_id] = level
    return level

# 5. КОНВЕЙЕР РАСЧЕТА ИЕРАРХИЧЕСКИХ МЕТРИК НА ВСЕ СТРОКИ
level_cache = {}
df_clean['level'] = df_clean['emp_id'].apply(lambda x: get_hierarchy_level(x, manager_map, level_cache))

# 6. СОРТИРОВКА И ФОРМИРОВАНИЕ ФИНАЛЬНОЙ ВИТРИНЫ ОРГСТРУКТУРЫ
final_view = df_clean.sort_values(by='level', ascending=True)
final_view = final_view[['emp_id', 'emp_name', 'manager_id', 'level']]
final_view.columns = ['ID Сотрудника', 'Имя', 'ID Начальника', 'Уровень Иерархии']
