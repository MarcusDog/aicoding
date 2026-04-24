DELETE FROM operation_log;
DELETE FROM message_notice;
DELETE FROM service_hours_record;
DELETE FROM activity_sign;
DELETE FROM activity_signup;
DELETE FROM notice;
DELETE FROM volunteer_activity;
DELETE FROM dict_activity_category;
DELETE FROM sys_user;
DELETE FROM student;
DELETE FROM admin_user;

INSERT INTO admin_user (id, admin_no, name, phone, email, title_name, admin_status, created_at, updated_at, is_deleted) VALUES
(1, 'A1001', '系统管理员', '13800000001', 'admin1@lida.edu.cn', '校团委老师', 'NORMAL', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, 'A1002', '学院管理员', '13800000002', 'admin2@lida.edu.cn', '辅导员', 'NORMAL', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO student (id, student_no, name, gender, college_name, major_name, class_name, phone, email, avatar_url, total_service_hours, student_status, remark, created_at, updated_at, is_deleted) VALUES
(1, '202209501', '王冠超', '男', '数字科学学院', '数据科学与大数据技术', '22大数据五班', '13900000001', '202209501@lida.edu.cn', NULL, 12.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, '202209502', '李思雨', '女', '数字科学学院', '数据科学与大数据技术', '22大数据五班', '13900000002', '202209502@lida.edu.cn', NULL, 8.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(3, '202209503', '陈宇航', '男', '数字科学学院', '计算机科学与技术', '22计科二班', '13900000003', '202209503@lida.edu.cn', NULL, 6.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(4, '202209504', '赵雨晴', '女', '数字科学学院', '计算机科学与技术', '22计科二班', '13900000004', '202209504@lida.edu.cn', NULL, 10.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(5, '202209505', '刘浩然', '男', '数字科学学院', '软件工程', '22软工一班', '13900000005', '202209505@lida.edu.cn', NULL, 4.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(6, '202209506', '孙若琳', '女', '数字科学学院', '软件工程', '22软工一班', '13900000006', '202209506@lida.edu.cn', NULL, 7.50, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(7, '202209507', '周子墨', '男', '管理学院', '市场营销', '22营销三班', '13900000007', '202209507@lida.edu.cn', NULL, 3.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(8, '202209508', '吴佳宁', '女', '管理学院', '市场营销', '22营销三班', '13900000008', '202209508@lida.edu.cn', NULL, 2.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(9, '202209509', '郑凯文', '男', '艺术设计学院', '视觉传达设计', '22视传一班', '13900000009', '202209509@lida.edu.cn', NULL, 5.50, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(10, '202209510', '许梦瑶', '女', '艺术设计学院', '环境设计', '22环设二班', '13900000010', '202209510@lida.edu.cn', NULL, 9.00, 'NORMAL', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO sys_user (id, username, password_hash, role_code, ref_id, account_status, last_login_time, created_at, updated_at, is_deleted) VALUES
(1, 'A1001', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'ADMIN', 1, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, 'A1002', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'ADMIN', 2, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(101, '202209501', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 1, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(102, '202209502', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 2, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(103, '202209503', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 3, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(104, '202209504', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 4, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(105, '202209505', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 5, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(106, '202209506', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 6, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(107, '202209507', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 7, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(108, '202209508', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 8, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(109, '202209509', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 9, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(110, '202209510', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'STUDENT', 10, 'ENABLED', NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO dict_activity_category (id, category_code, category_name, sort_no, category_status, created_at, updated_at) VALUES
(1, 'CAMPUS', '校园服务', 1, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(2, 'COMMUNITY', '社区服务', 2, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(3, 'SPORT', '赛事服务', 3, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(4, 'PUBLICITY', '公益宣传', 4, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(5, 'ENV', '环保服务', 5, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(6, 'CARE', '关爱帮扶', 6, 'ENABLED', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO volunteer_activity (id, title, category_code, location, organizer_name, description, cover_url, attachment_url, recruit_count, signup_deadline, start_time, end_time, service_hours, check_in_code, check_out_code, activity_status, published_by, published_at, created_at, updated_at, is_deleted) VALUES
(1, '图书馆志愿整理', 'CAMPUS', '图书馆一楼服务台', '校团委', '协助图书整理与借阅秩序维护', NULL, NULL, 20, DATEADD('DAY', 1, CURRENT_TIMESTAMP()), DATEADD('DAY', 2, CURRENT_TIMESTAMP()), DATEADD('DAY', 2, DATEADD('HOUR', 4, CURRENT_TIMESTAMP())), 4.00, 'LIB001', 'LIB002', 'PUBLISHED', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, '社区敬老志愿活动', 'COMMUNITY', '浦东新区社区服务中心', '青年志愿者协会', '陪伴老人并协助开展文娱活动', NULL, NULL, 15, DATEADD('DAY', 2, CURRENT_TIMESTAMP()), DATEADD('DAY', 4, CURRENT_TIMESTAMP()), DATEADD('DAY', 4, DATEADD('HOUR', 3, CURRENT_TIMESTAMP())), 3.00, 'OLD001', 'OLD002', 'PUBLISHED', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(3, '校园环保宣传周', 'ENV', '综合楼大厅', '后勤处', '进行垃圾分类与低碳宣传', NULL, NULL, 30, DATEADD('DAY', -3, CURRENT_TIMESTAMP()), DATEADD('DAY', -2, CURRENT_TIMESTAMP()), DATEADD('DAY', -2, DATEADD('HOUR', 2, CURRENT_TIMESTAMP())), 2.00, 'ENV001', 'ENV002', 'COMPLETED', 2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(4, '校运动会志愿服务', 'SPORT', '体育场', '体育教学部', '负责检录和赛事服务', NULL, NULL, 40, DATEADD('DAY', 5, CURRENT_TIMESTAMP()), DATEADD('DAY', 10, CURRENT_TIMESTAMP()), DATEADD('DAY', 10, DATEADD('HOUR', 8, CURRENT_TIMESTAMP())), 8.00, 'SPT001', 'SPT002', 'PUBLISHED', 2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(5, '新生报到引导', 'CAMPUS', '校门口', '学生处', '为新生提供入学报到引导', NULL, NULL, 25, DATEADD('DAY', -12, CURRENT_TIMESTAMP()), DATEADD('DAY', -10, CURRENT_TIMESTAMP()), DATEADD('DAY', -10, DATEADD('HOUR', 6, CURRENT_TIMESTAMP())), 6.00, 'NEW001', 'NEW002', 'COMPLETED', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO notice (id, title, content, attachment_url, target_scope, publish_status, published_by, published_at, created_at, updated_at, is_deleted) VALUES
(1, '志愿者时长认定说明', '请同学们在活动结束后及时关注个人时长确认情况。', NULL, 'ALL_STUDENTS', 'PUBLISHED', 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, '系统试运行公告', '大学生志愿者管理系统已进入试运行阶段。', NULL, 'ALL_STUDENTS', 'PUBLISHED', 2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO activity_signup (id, activity_id, student_id, signup_status, review_comment, reviewed_by, reviewed_at, cancel_reason, signup_time, created_at, updated_at, is_deleted) VALUES
(1, 1, 1, 'APPROVED', '符合要求', 1, CURRENT_TIMESTAMP(), NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(2, 1, 2, 'PENDING', NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(3, 2, 3, 'APPROVED', '通过', 1, CURRENT_TIMESTAMP(), NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(4, 3, 4, 'APPROVED', '通过', 2, CURRENT_TIMESTAMP(), NULL, DATEADD('DAY', -4, CURRENT_TIMESTAMP()), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(5, 3, 5, 'APPROVED', '通过', 2, CURRENT_TIMESTAMP(), NULL, DATEADD('DAY', -4, CURRENT_TIMESTAMP()), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0),
(6, 5, 6, 'APPROVED', '通过', 1, CURRENT_TIMESTAMP(), NULL, DATEADD('DAY', -12, CURRENT_TIMESTAMP()), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), 0);

INSERT INTO activity_sign (id, activity_id, student_id, sign_status, sign_in_time, sign_out_time, sign_in_mode, sign_out_mode, sign_in_operator_id, sign_out_operator_id, exception_remark, created_at, updated_at) VALUES
(1, 1, 1, 'UNSIGNED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(2, 2, 3, 'UNSIGNED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(3, 3, 4, 'SIGNED_OUT', DATEADD('DAY', -2, CURRENT_TIMESTAMP()), DATEADD('DAY', -2, DATEADD('HOUR', 2, CURRENT_TIMESTAMP())), 'CODE', 'CODE', NULL, NULL, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(4, 3, 5, 'ADMIN_FIXED', DATEADD('DAY', -2, CURRENT_TIMESTAMP()), DATEADD('DAY', -2, DATEADD('HOUR', 2, CURRENT_TIMESTAMP())), 'ADMIN', 'ADMIN', 2, 2, '管理员补录', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(5, 5, 6, 'SIGNED_OUT', DATEADD('DAY', -10, CURRENT_TIMESTAMP()), DATEADD('DAY', -10, DATEADD('HOUR', 6, CURRENT_TIMESTAMP())), 'CODE', 'CODE', NULL, NULL, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO service_hours_record (id, activity_id, student_id, signup_id, sign_id, hours_value, hours_status, generated_at, confirmed_by, confirmed_at, remark, created_at, updated_at) VALUES
(1, 3, 4, 4, 3, 2.00, 'CONFIRMED', CURRENT_TIMESTAMP(), 2, CURRENT_TIMESTAMP(), '正常完成', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(2, 3, 5, 5, 4, 2.00, 'CONFIRMED', CURRENT_TIMESTAMP(), 2, CURRENT_TIMESTAMP(), '补录确认', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
(3, 5, 6, 6, 5, 6.00, 'CONFIRMED', CURRENT_TIMESTAMP(), 1, CURRENT_TIMESTAMP(), '正常完成', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO message_notice (id, user_id, message_type, title, content, biz_type, biz_id, is_read, created_at, read_at) VALUES
(1, 101, 'NOTICE_PUBLISHED', '新公告通知', '志愿者时长认定说明', 'NOTICE', 1, 0, CURRENT_TIMESTAMP(), NULL),
(2, 104, 'HOURS_CONFIRMED', '时长确认通知', '你的服务时长已确认', 'HOURS', 1, 0, CURRENT_TIMESTAMP(), NULL),
(3, 106, 'HOURS_CONFIRMED', '时长确认通知', '你的服务时长已确认', 'HOURS', 3, 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

INSERT INTO operation_log (id, operator_user_id, operator_role_code, module_name, operation_type, biz_id, request_path, operation_desc, operation_time) VALUES
(1, 1, 'ADMIN', 'ACTIVITY', 'PUBLISH', 1, '/api/admin/activities/1/publish', '发布图书馆志愿整理活动', CURRENT_TIMESTAMP()),
(2, 2, 'ADMIN', 'HOURS', 'CONFIRM', 1, '/api/admin/hours/1/confirm', '确认学生时长', CURRENT_TIMESTAMP());
