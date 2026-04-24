# 数据库设计与优化

## 核心表

- `admin`：管理员
- `user`：员工/用户
- `face_data`：人脸特征
- `check_rule`：签到规则
- `attendance_record`：签到记录
- `operation_log`：操作日志

## 关键关系

- `user 1 - 1 face_data`
- `user 1 - N attendance_record`
- `check_rule 1 - N attendance_record`
- `admin 1 - N check_rule`

## 已做的性能优化

- 用户检索索引：`idx_user_name`、`idx_user_department_status`
- 签到查询索引：`idx_attendance_user_time`、`idx_attendance_rule_time`、`idx_attendance_status_time`
- 规则索引：`idx_check_rule_active`、`idx_check_rule_admin_active`
- 日志索引：`idx_operation_created`、`idx_operation_operator`

## 执行方式

```bash
python scripts/db_optimize.py
```

说明：脚本会尝试创建索引，已存在则跳过。
