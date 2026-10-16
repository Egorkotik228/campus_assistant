import os
from sqlalchemy import create_engine

DB_USER = os.getenv('DB_USER', 'egorcernysov')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Egor_kill228')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '1234')
DB_NAME = os.getenv('DB_NAME', 'campus_assistant')

connection_string = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

sql_create_views = """
-- Удаляем старые витрины, чтобы избежать конфликтов типов данных
DROP VIEW IF EXISTS public.v_full_schedule CASCADE;
DROP VIEW IF EXISTS public.v_teacher_details CASCADE;
DROP VIEW IF EXISTS public.v_rooms_navigation CASCADE;

-- Создаем витрину 1: Полное расписание
CREATE VIEW public.v_full_schedule AS
SELECT 
    fl.lesson_id,
    fl.group_name,
    dg.course,
    fl.weekday_no_or_exam_date,
    fl.pair_number,
    dpt.start_time,
    dpt.end_time,
    ds.subject_name,
    fl.lesson_type,
    COALESCE(dt.full_name, 'Не указан') AS teacher_name,
    COALESCE(dt.department, 'Не указана') AS teacher_department,
    fl.auditory_titles,
    fl.location,
    fl.date_from,
    fl.date_to,
    fl.is_session
FROM public.fact_lessons fl
LEFT JOIN public.dim_groups dg 
    ON fl.group_name = dg.group_name
LEFT JOIN public.dim_subjects ds 
    ON fl.subject_id = ds.subject_id
LEFT JOIN public.dim_teachers dt 
    ON fl.teacher_id = dt.teacher_id
LEFT JOIN public.dim_pair_times dpt 
    ON fl.pair_number = dpt.pair_no 
    AND (CASE WHEN dg.evening THEN 1 ELSE 0 END) = dpt.evening_code;

-- Создаем витрину 2: Карточки преподавателей
CREATE VIEW public.v_teacher_details AS
SELECT 
    dt.teacher_id,
    dt.full_name,
    COALESCE(dt.department, 'Не указана') AS department,
    COALESCE(dt.position, 'Не указана') AS position,
    COALESCE(dt.email, 'Не указан') AS email,
    COALESCE(STRING_AGG(ds.subject_name, ', ' ORDER BY ds.subject_name), 'Нет привязанных дисциплин') AS subjects_list
FROM public.dim_teachers dt
LEFT JOIN public.rel_teacher_subjects rts 
    ON dt.teacher_id = rts.teacher_id
LEFT JOIN public.dim_subjects ds 
    ON rts.subject_id = ds.subject_id
GROUP BY dt.teacher_id, dt.full_name, dt.department, dt.position, dt.email;

-- Создаем витрину 3: Навигация по аудиториям
CREATE VIEW public.v_rooms_navigation AS
SELECT 
    dr.room_id,
    dr.room_as_in_source AS room_number,
    dr.location_value_in_schedule AS location_name,
    COALESCE(db.building_id, dr.building_id_by_room_prefix) AS building_code,
    db.name AS building_full_name,
    db.address,
    db.transport
FROM public.dim_rooms dr
LEFT JOIN public.dim_buildings db 
    ON COALESCE(dr.building_id_by_location, dr.building_id_by_room_prefix) = db.building_id;
"""

if __name__ == '__main__':
    with engine.begin() as conn:
        conn.exec_driver_sql(sql_create_views)
    print("Витрины успешно созданы")
