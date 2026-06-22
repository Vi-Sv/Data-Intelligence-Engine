# КЕЙС №5: АНАЛИЗ И СЕГМЕНТАЦИЯ ПРОИЗВОДСТВЕННОГО БРАКА ПО ЛИНИЯМ (БЛОК: ОТК)
# Реализация конвейера нормализации, очистки и пост-фильтрации данных через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ДАННЫХ
df = pd.read_sql("SELECT * FROM raw_manufacture", con=engine)

# 2. ПЕРВИЧНАЯ ФИЛЬТРАЦИЯ И СТАНДАРТИЗАЦИЯ ТЕКСТА (Аналог WHERE)
# Удаляем пробелы и переводим комментарии ОТК в нижний регистр для точного совпадения
df['inspector_comment'] = df['inspector_comment'].astype(str).str.strip().str.lower()
df_filtered = df[df['inspector_comment'] == 'брак'].copy()

# 3. НОРМАЛИЗАЦИЯ ИДЕНТИФИКАТОРОВ И ВАЛИДАЦИЯ МЕТРИК
# Очищаем номера линий от скрытых концевых пробелов
df_filtered['line_id'] = df_filtered['line_id'].astype(str).str.strip()
# Заменяем пропуски NULL в счетчиках брака нулями (Аналог COALESCE)
df_filtered['defect_count'] = df_filtered['defect_count'].fillna(0).astype(int)

# 4. АГРЕГАЦИЯ ДАННЫХ ПО ПРОИЗВОДСТВЕННЫМ ЛИНИЯМ (Аналог GROUP BY + SUM)
line_stats = df_filtered.groupby('line_id')['defect_count'].sum().reset_index()
line_stats.columns = ['line_id', 'total_defect_count']

# 5. ПОСТ-ФИЛЬТРАЦИЯ АГРЕГИРОВАННЫХ ПОКАЗАТЕЛЕЙ (Аналог HAVING)
# Выделяем только аварийные линии, превысившие критический порог в 15 000 единиц брака
final_view = line_stats[line_stats['total_defect_count'] > 15000]

# 6. ОФОРМЛЕНИЕ ФИНАЛЬНОЙ ВИТРИНЫ
final_view.columns = ['Номер производственной линии', 'Суммарный объем брака (шт)']
