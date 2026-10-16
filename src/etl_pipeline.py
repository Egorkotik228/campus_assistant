import os
import pandas as pd
from sqlalchemy import create_engine

# 1) Подключение к базе данных
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '1234')
DB_NAME = os.getenv('DB_NAME', 'campus_assistant')

connection_string = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

base = os.path.expanduser('~/Desktop/campus_assistant/data/raw/extracted/data')

# 2) Предобработка dim_groups
df_groups = pd.read_csv(os.path.join(base, 'schedule/groups.csv'), encoding='utf-8-sig')
df_groups = df_groups.rename(columns={'group': 'group_name'})
df_groups = df_groups.drop(columns=['comment'])
df_groups['course'] = df_groups['course'].astype('Int64')
df_groups['evening'] = df_groups['evening'].astype('boolean')
df_groups['date_from'] = pd.to_datetime(df_groups['date_from'], errors='coerce').dt.date
df_groups['date_to'] = pd.to_datetime(df_groups['date_to'], errors='coerce').dt.date
df_groups = df_groups.drop_duplicates(subset=['group_name'])

# 3) Предобработка dim_subjects
df_subjects_raw = pd.read_csv(os.path.join(base, 'schedule/subjects.csv'), encoding='utf-8-sig')
df_subjects = df_subjects_raw[['subject_id', 'subject']].rename(columns={'subject': 'subject_name'}).copy()
df_subjects['subject_name'] = df_subjects['subject_name'].astype(str).str.strip()
df_subjects = df_subjects.drop_duplicates(subset=['subject_id'])

# 4) Предобработка dim_lesson_types
df_lesson_types = pd.read_csv(os.path.join(base, 'schedule/lesson_types.csv'), encoding='utf-8-sig')
df_lesson_types = df_lesson_types[['lesson_type', 'suffix_eor_in_source', 'note']].copy()
df_lesson_types['lesson_type'] = df_lesson_types['lesson_type'].astype(str).str.strip()
df_lesson_types = df_lesson_types.drop_duplicates(subset=['lesson_type'])

# 5) Предобработка dim_teachers
df_teachers = pd.read_csv(os.path.join(base, 'teachers/teachers.csv'), encoding='utf-8-sig')
df_teachers = df_teachers.rename(columns={'name': 'full_name'})
df_teachers = df_teachers[[
    'teacher_id', 'full_name', 'department', 'position', 'email', 'info_source_url'
]].copy()
df_teachers['full_name'] = df_teachers['full_name'].astype(str).str.strip()
df_teachers = df_teachers.drop_duplicates(subset=['teacher_id'])

# 6) Предобработка dim_buildings
df_buildings = pd.read_csv(os.path.join(base, 'buildings/buildings.csv'), encoding='utf-8-sig')
df_buildings = df_buildings.drop_duplicates(subset=['building_id'])

# 7) Предобработка dim_rooms
df_rooms = pd.read_csv(os.path.join(base, 'rooms/rooms.csv'), encoding='utf-8-sig')
df_rooms = df_rooms[[
    'location_value_in_schedule', 'building_id_by_location',
    'room_as_in_source', 'building_id_by_room_prefix'
]].copy()
df_rooms['room_as_in_source'] = df_rooms['room_as_in_source'].astype(str).str.strip()
df_rooms = df_rooms.drop_duplicates()

# 8) Предобработка dim_pair_times
df_pair_times = pd.read_csv(os.path.join(base, 'schedule/pair_times.csv'), encoding='utf-8-sig')
df_pair_times = df_pair_times.rename(columns={
    'start': 'start_time',
    'end': 'end_time',
    'source': 'source_info'
})
df_pair_times = df_pair_times.drop_duplicates(subset=['evening_code', 'pair_no'])

# 9) Предобработка rel_teacher_subjects
rel_rows = []
for _, row in df_subjects_raw[['subject_id', 'teacher_ids']].dropna().iterrows():
    s_id = row['subject_id']
    for tid in str(row['teacher_ids']).split(';'):
        tid_clean = tid.strip()
        if tid_clean.isdigit():
            rel_rows.append({'subject_id': int(s_id), 'teacher_id': int(tid_clean)})

df_rel_teacher_subjects = pd.DataFrame(rel_rows)
df_rel_teacher_subjects = df_rel_teacher_subjects[
    df_rel_teacher_subjects['subject_id'].isin(df_subjects['subject_id']) &
    df_rel_teacher_subjects['teacher_id'].isin(df_teachers['teacher_id'])
].drop_duplicates(subset=['teacher_id', 'subject_id'])

# 10) Предобработка fact_lessons
df_sem = pd.read_csv(os.path.join(base, 'schedule/lessons_semester.csv'), encoding='utf-8-sig')
df_sem['is_session'] = False

df_ses = pd.read_csv(os.path.join(base, 'schedule/exams_session.csv'), encoding='utf-8-sig')
df_ses['is_session'] = True

df_schedule = pd.concat([df_sem, df_ses], ignore_index=True)
df_schedule = df_schedule.rename(columns={'group': 'group_name', 'pair_no': 'pair_number'})

df_schedule['group_name'] = df_schedule['group_name'].astype(str).str.strip()
df_schedule['subject'] = df_schedule['subject'].astype(str).str.strip()
df_schedule['lesson_type'] = df_schedule['lesson_type'].astype(str).str.strip()

df_schedule = df_schedule.merge(
    df_subjects[['subject_id', 'subject_name']],
    left_on='subject',
    right_on='subject_name',
    how='left'
)

def parse_teacher_id(val):
    if pd.isna(val):
        return None
    for p in str(val).split(';'):
        p_clean = p.strip()
        if p_clean.isdigit():
            return int(p_clean)
    return None

df_schedule['teacher_id'] = df_schedule['teacher_ids'].apply(parse_teacher_id).astype('Int64')
df_schedule['pair_number'] = pd.to_numeric(df_schedule['pair_number'], errors='coerce').astype('Int64')
df_schedule['date_from'] = pd.to_datetime(df_schedule['date_from'], errors='coerce').dt.date
df_schedule['date_to'] = pd.to_datetime(df_schedule['date_to'], errors='coerce').dt.date

fact_cols = [
    'group_name', 'subject_id', 'teacher_id', 'pair_number',
    'lesson_type', 'weekday_no_or_exam_date', 'location',
    'auditory_titles', 'date_from', 'date_to', 'is_session'
]
df_fact_lessons = df_schedule[fact_cols].copy()

# внешние ключи
df_fact_lessons = df_fact_lessons[df_fact_lessons['group_name'].isin(df_groups['group_name'])].copy()
df_fact_lessons.loc[~df_fact_lessons['teacher_id'].isin(df_teachers['teacher_id']), 'teacher_id'] = None
df_fact_lessons.loc[~df_fact_lessons['lesson_type'].isin(df_lesson_types['lesson_type']), 'lesson_type'] = None

# 11) Загрузка таблиц в PostgreSQL
with engine.begin() as conn:
    tables_to_load = [
        ('dim_groups', df_groups),
        ('dim_subjects', df_subjects),
        ('dim_lesson_types', df_lesson_types),
        ('dim_teachers', df_teachers),
        ('dim_buildings', df_buildings),
        ('dim_rooms', df_rooms),
        ('dim_pair_times', df_pair_times),
        ('rel_teacher_subjects', df_rel_teacher_subjects),
        ('fact_lessons', df_fact_lessons)
    ]

    for table_name, df_data in tables_to_load:
        cnt = pd.read_sql(f"SELECT count(*) as cnt FROM public.{table_name};", con=conn).iloc[0]['cnt']
        if cnt == 0:
            df_data.to_sql(table_name, con=conn, schema='public', if_exists='append', index=False)
            print(f"{table_name}: успешно загружено {len(df_data)} строк")
        else:
            print(f"{table_name}: уже содержит {cnt} строк, шаг пропущен")

print("\nПайплайн успешно завершил работу.")