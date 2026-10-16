import os
import pandas as pd
from sqlalchemy import create_engine

# 1) Подключение к БД
DB_USER = 'egorcernysov'
DB_PASSWORD = 'секрет'
DB_HOST = 'localhost'
DB_PORT = '1234'
DB_NAME = 'campus_assistant'

connection_string = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

try:
    with engine.connect() as connection:
        print('Успешно подключились к PostgreSQL\n')
except Exception as e:
    print(f'Босс, у нас ошибка: {e}\n')

base = os.path.expanduser('~/Desktop/campus_assistant/data/raw/extracted/data')

csv_files = {
    'Groups (Группы)': 'schedule/groups.csv',
    'Subjects (Предметы)': 'schedule/subjects.csv',
    'Lesson Types (Типы занятий)': 'schedule/lesson_types.csv',
    'Teachers (Преподаватели)': 'teachers/teachers.csv',
    'Buildings (Корпуса)': 'buildings/buildings.csv',
    'Rooms (Аудитории)': 'rooms/rooms.csv',
    'Pair Times (Звонки)': 'schedule/pair_times.csv',
    'Lessons Semester (Семестр)': 'schedule/lessons_semester.csv',
    'Exams Session (Сессия)': 'schedule/exams_session.csv'
}

for label, rel_path in csv_files.items():
    path = os.path.join(base, rel_path)
    print("=" * 70)
    print(f"--- АУДИТ: {label} ---")
    print("=" * 70)

    if os.path.exists(path):
        try:
            df = pd.read_csv(path, encoding='utf-8-sig')
            print(f"Путь: {path}")
            print(f"Всего строк: {len(df)}")
            print("\n--- Первые строки (head 3) ---")
            print(df.head(3))
            print("\n--- Колонки и типы данных ---")
            print(df.dtypes)
            print("\n")
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}\n")
    else:
        print(f"[!] Файл не найден по пути: {path}\n")
