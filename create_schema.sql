DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

CREATE TABLE public.dim_groups (
    group_name VARCHAR(50) PRIMARY KEY,
    course INT,
    evening BOOLEAN,
    date_from DATE,
    date_to DATE,
    flag_in_groups_list BOOLEAN,
    is_in_session_now BOOLEAN,
    has_session_schedule BOOLEAN,
    has_semester_data BOOLEAN
);

CREATE TABLE public.dim_subjects (
    subject_id INT PRIMARY KEY,
    subject_name TEXT NOT NULL
);

CREATE TABLE public.dim_lesson_types (
    lesson_type VARCHAR(100) PRIMARY KEY,
    suffix_eor_in_source BOOLEAN,
    note TEXT
);


CREATE TABLE public.dim_teachers (
    teacher_id INT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT,
    position TEXT,
    email VARCHAR(255),
    info_source_url TEXT
);

CREATE TABLE public.dim_buildings (
    building_id VARCHAR(20) PRIMARY KEY,
    codes_in_room_names VARCHAR(50),
    name TEXT NOT NULL,
    address TEXT,
    index_city VARCHAR(50),
    transport TEXT,
    source_url TEXT,
    location_value_in_schedule VARCHAR(100)
);


CREATE TABLE public.dim_rooms (
    room_id SERIAL PRIMARY KEY,
    location_value_in_schedule VARCHAR(100),
    building_id_by_location VARCHAR(20) REFERENCES public.dim_buildings(building_id),
    room_as_in_source VARCHAR(100) NOT NULL,
    building_id_by_room_prefix VARCHAR(20) REFERENCES public.dim_buildings(building_id)
);


CREATE TABLE public.dim_pair_times (
    evening_code INT,
    pair_no INT,
    start_time VARCHAR(5) NOT NULL,
    end_time VARCHAR(5) NOT NULL,
    source_info TEXT,
    PRIMARY KEY (evening_code, pair_no)
);


CREATE TABLE public.rel_teacher_subjects (
    teacher_id INT REFERENCES public.dim_teachers(teacher_id) ON DELETE CASCADE,
    subject_id INT REFERENCES public.dim_subjects(subject_id) ON DELETE CASCADE,
    PRIMARY KEY (teacher_id, subject_id)
);

CREATE TABLE public.fact_lessons (
    lesson_id SERIAL PRIMARY KEY,
    group_name VARCHAR(50) REFERENCES public.dim_groups(group_name) ON DELETE CASCADE,
    subject_id INT REFERENCES public.dim_subjects(subject_id) ON DELETE SET NULL,
    teacher_id INT REFERENCES public.dim_teachers(teacher_id) ON DELETE SET NULL,
    pair_number INT,
    lesson_type VARCHAR(100) REFERENCES public.dim_lesson_types(lesson_type) ON DELETE SET NULL,
    weekday_no_or_exam_date VARCHAR(50),
    location TEXT,
    auditory_titles TEXT,
    date_from DATE,
    date_to DATE,
    is_session BOOLEAN NOT NULL DEFAULT FALSE
);

