import os
from sqlalchemy import create_engine, text

# Настройки подключения
DB_USER = os.getenv('DB_USER', 'egorcernysov')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '1234')
DB_NAME = os.getenv('DB_NAME', 'campus_assistant')

connection_string = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)


# 1. Получить расписание группы
def get_group_schedule(group_name: str, day_or_date: str = None, is_session: bool = False) -> list[dict]:
    query = """
        SELECT 
            group_name, course, weekday_no_or_exam_date, pair_number,
            start_time, end_time, subject_name, lesson_type,
            teacher_name, auditory_titles, location, date_from, date_to
        FROM public.v_full_schedule
        WHERE group_name = :grp AND is_session = :ses
    """
    params = {'grp': group_name.strip(), 'ses': is_session}

    if day_or_date:
        query += " AND weekday_no_or_exam_date = :day"
        params['day'] = str(day_or_date).strip()

    query += " ORDER BY weekday_no_or_exam_date, pair_number;"

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]


# 2. Найти карточку преподавателя и список всех его дисциплин
def get_teacher_info(teacher_name_query: str) -> list[dict]:
    query = text("""
        SELECT teacher_id, full_name, department, position, email, subjects_list
        FROM public.v_teacher_details
        WHERE full_name ILIKE :name
        ORDER BY full_name
        LIMIT 5;
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {'name': f"%{teacher_name_query.strip()}%"})
        return [dict(row._mapping) for row in result]


# 3. Навигация по аудитории или корпусу
def get_room_navigation(room_query: str) -> list[dict]:
    query = text("""
        SELECT room_number, location_name, building_code, building_full_name, address, transport
        FROM public.v_rooms_navigation
        WHERE room_number ILIKE :rm OR building_code ILIKE :rm
        LIMIT 5;
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {'rm': f"%{room_query.strip()}%"})
        return [dict(row._mapping) for row in result]


# Локальный тест функций
if __name__ == '__main__':
    print("1. Тест расписания группы 221-811 на вторник (день 2):")
    print(get_group_schedule('221-811', day_or_date='2')[:2])

    print("\n2. Тест карточки преподавателя (Зайцев):")
    print(get_teacher_info('Зайцев'))

    print("\n3. Тест навигации по аудитории (Д108):")
    print(get_room_navigation('Д108'))
