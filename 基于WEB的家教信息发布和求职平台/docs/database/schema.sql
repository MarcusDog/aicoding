CREATE DATABASE IF NOT EXISTS tutor_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tutor_platform;

CREATE TABLE user_account (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  display_name VARCHAR(64) NOT NULL,
  phone VARCHAR(32),
  role VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutor_profile (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL UNIQUE,
  school VARCHAR(128) NOT NULL,
  major VARCHAR(128) NOT NULL,
  subjects VARCHAR(255) NOT NULL,
  introduction VARCHAR(1000),
  teaching_experience_years INT NOT NULL DEFAULT 0,
  service_mode VARCHAR(64) NOT NULL,
  resume_text VARCHAR(3000),
  resume_file_name VARCHAR(255),
  resume_file_path VARCHAR(500),
  resume_file_content_type VARCHAR(128),
  resume_file_size BIGINT,
  review_remark VARCHAR(500),
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_tutor_profile_user FOREIGN KEY (user_id) REFERENCES user_account(id)
);

CREATE TABLE tutor_demand (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  parent_id BIGINT NOT NULL,
  title VARCHAR(128) NOT NULL,
  subject VARCHAR(64) NOT NULL,
  grade_level VARCHAR(64) NOT NULL,
  location VARCHAR(128) NOT NULL,
  budget_min DECIMAL(10, 2) NOT NULL,
  budget_max DECIMAL(10, 2) NOT NULL,
  schedule VARCHAR(128) NOT NULL,
  description VARCHAR(1000),
  review_remark VARCHAR(500),
  status VARCHAR(30) NOT NULL DEFAULT 'PENDING_REVIEW',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_tutor_demand_parent FOREIGN KEY (parent_id) REFERENCES user_account(id)
);

CREATE TABLE tutor_application (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  demand_id BIGINT NOT NULL,
  tutor_id BIGINT NOT NULL,
  cover_letter VARCHAR(1000),
  review_remark VARCHAR(500),
  status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_application_demand_tutor UNIQUE (demand_id, tutor_id),
  CONSTRAINT fk_application_demand FOREIGN KEY (demand_id) REFERENCES tutor_demand(id),
  CONSTRAINT fk_application_tutor FOREIGN KEY (tutor_id) REFERENCES user_account(id)
);

CREATE TABLE tutor_order (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  demand_id BIGINT NOT NULL UNIQUE,
  application_id BIGINT NOT NULL UNIQUE,
  parent_id BIGINT NOT NULL,
  tutor_id BIGINT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_order_demand FOREIGN KEY (demand_id) REFERENCES tutor_demand(id),
  CONSTRAINT fk_order_application FOREIGN KEY (application_id) REFERENCES tutor_application(id),
  CONSTRAINT fk_order_parent FOREIGN KEY (parent_id) REFERENCES user_account(id),
  CONSTRAINT fk_order_tutor FOREIGN KEY (tutor_id) REFERENCES user_account(id)
);

CREATE TABLE audit_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  target_type VARCHAR(64) NOT NULL,
  target_id BIGINT NOT NULL,
  action VARCHAR(64) NOT NULL,
  result VARCHAR(32) NOT NULL,
  remark VARCHAR(1000),
  reviewer_id BIGINT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_audit_reviewer FOREIGN KEY (reviewer_id) REFERENCES user_account(id)
);
