CREATE TABLE IF NOT EXISTS student (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    college_name VARCHAR(100) NOT NULL,
    major_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    avatar_url VARCHAR(255),
    total_service_hours DECIMAL(6,2) DEFAULT 0.00,
    student_status VARCHAR(20) DEFAULT 'NORMAL',
    remark VARCHAR(255),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS admin_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    title_name VARCHAR(100),
    admin_status VARCHAR(20) DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role_code VARCHAR(20) NOT NULL,
    ref_id BIGINT NOT NULL,
    account_status VARCHAR(20) DEFAULT 'ENABLED',
    last_login_time DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0,
    UNIQUE (role_code, ref_id)
);

CREATE TABLE IF NOT EXISTS dict_activity_category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(20) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL,
    sort_no INT DEFAULT 0,
    category_status VARCHAR(20) DEFAULT 'ENABLED',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS volunteer_activity (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    category_code VARCHAR(20) NOT NULL,
    location VARCHAR(255) NOT NULL,
    organizer_name VARCHAR(100) NOT NULL,
    description TEXT,
    cover_url VARCHAR(255),
    attachment_url VARCHAR(255),
    recruit_count INT NOT NULL,
    signup_deadline DATETIME NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    service_hours DECIMAL(6,2) NOT NULL,
    check_in_code VARCHAR(20),
    check_out_code VARCHAR(20),
    activity_status VARCHAR(20) DEFAULT 'DRAFT',
    published_by BIGINT,
    published_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0,
    CONSTRAINT fk_activity_category FOREIGN KEY (category_code) REFERENCES dict_activity_category(category_code),
    CONSTRAINT fk_activity_published_by FOREIGN KEY (published_by) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS notice (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    attachment_url VARCHAR(255),
    target_scope VARCHAR(20) DEFAULT 'ALL_STUDENTS',
    publish_status VARCHAR(20) DEFAULT 'PUBLISHED',
    published_by BIGINT NOT NULL,
    published_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0,
    CONSTRAINT fk_notice_published_by FOREIGN KEY (published_by) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS activity_signup (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    signup_status VARCHAR(20) DEFAULT 'PENDING',
    review_comment VARCHAR(255),
    reviewed_by BIGINT,
    reviewed_at DATETIME,
    cancel_reason VARCHAR(255),
    signup_time DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    is_deleted TINYINT DEFAULT 0,
    UNIQUE (activity_id, student_id),
    CONSTRAINT fk_signup_activity FOREIGN KEY (activity_id) REFERENCES volunteer_activity(id),
    CONSTRAINT fk_signup_student FOREIGN KEY (student_id) REFERENCES student(id),
    CONSTRAINT fk_signup_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS activity_sign (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    sign_status VARCHAR(20) DEFAULT 'UNSIGNED',
    sign_in_time DATETIME,
    sign_out_time DATETIME,
    sign_in_mode VARCHAR(20),
    sign_out_mode VARCHAR(20),
    sign_in_operator_id BIGINT,
    sign_out_operator_id BIGINT,
    exception_remark VARCHAR(255),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE (activity_id, student_id),
    CONSTRAINT fk_sign_activity FOREIGN KEY (activity_id) REFERENCES volunteer_activity(id),
    CONSTRAINT fk_sign_student FOREIGN KEY (student_id) REFERENCES student(id),
    CONSTRAINT fk_sign_operator_in FOREIGN KEY (sign_in_operator_id) REFERENCES sys_user(id),
    CONSTRAINT fk_sign_operator_out FOREIGN KEY (sign_out_operator_id) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS service_hours_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    signup_id BIGINT,
    sign_id BIGINT,
    hours_value DECIMAL(6,2) NOT NULL,
    hours_status VARCHAR(20) DEFAULT 'PENDING_CONFIRM',
    generated_at DATETIME NOT NULL,
    confirmed_by BIGINT,
    confirmed_at DATETIME,
    remark VARCHAR(255),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE (activity_id, student_id),
    CONSTRAINT fk_hours_activity FOREIGN KEY (activity_id) REFERENCES volunteer_activity(id),
    CONSTRAINT fk_hours_student FOREIGN KEY (student_id) REFERENCES student(id),
    CONSTRAINT fk_hours_signup FOREIGN KEY (signup_id) REFERENCES activity_signup(id),
    CONSTRAINT fk_hours_sign FOREIGN KEY (sign_id) REFERENCES activity_sign(id),
    CONSTRAINT fk_hours_confirmed_by FOREIGN KEY (confirmed_by) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS message_notice (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    content VARCHAR(255) NOT NULL,
    biz_type VARCHAR(50),
    biz_id BIGINT,
    is_read TINYINT DEFAULT 0,
    created_at DATETIME NOT NULL,
    read_at DATETIME,
    CONSTRAINT fk_message_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
);

CREATE TABLE IF NOT EXISTS operation_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    operator_user_id BIGINT NOT NULL,
    operator_role_code VARCHAR(20) NOT NULL,
    module_name VARCHAR(50) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    biz_id BIGINT,
    request_path VARCHAR(255),
    operation_desc VARCHAR(255),
    operation_time DATETIME NOT NULL,
    CONSTRAINT fk_log_operator FOREIGN KEY (operator_user_id) REFERENCES sys_user(id)
);
