import os
import pandas as pd

base = os.path.expanduser('~/Desktop/campus_assistant/data/raw/extracted/data')

files_to_check = {
    'buildings.csv': os.path.join(base, 'buildings/buildings.csv'),
    'rooms.csv': os.path.join(base, 'rooms/rooms.csv'),
    'pair_times.csv': os.path.join(base, 'schedule/pair_times.csv')
}

for name, path in files_to_check.items():
    print("=" * 60)
    print(f"ФАЙЛ: {name}")
    print("=" * 60)
    if not os.path.exists(path):
        print(f"Файл не найден по пути: {path}")
        continue
    df = pd.read_csv(path, encoding='utf-8-sig')
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        null_count = df[col].isna().sum()
        print(f"[{col}] | Тип: {df[col].dtype} | Пропусков: {null_count}/{len(df)}")
        if len(unique_vals) <= 3:
            print(f"   Значения: {list(unique_vals)}")
        else:
            print(f"   Примеры: {list(unique_vals[:2])}")
    print()
