# API 文档

Base URL：`/api`（本地直连时为 `http://localhost:5000/api`）

## 统一返回格式

```json
{
  "success": true,
  "message": "success",
  "data": {}
}
```

## 认证

- `POST /auth/wx-login`：微信登录（开发模式或真实 code2session）
- `POST /auth/admin-login`：管理员登录
- `POST /auth/logout`：退出登录
- `GET /auth/profile`：当前登录用户信息

## 用户侧

- `GET /user/me`：获取用户资料
- `PUT /user/me`：更新用户资料

## 人脸管理

- `GET /face/status`：查询注册状态
- `POST /face/register`：注册人脸
- `PUT /face/update`：更新人脸
- `POST /face/verify`：1:1 验证
- `GET /face/liveness-command`：获取活体动作指令
- `POST /face/liveness-verify`：活体验证（动作 + 多帧）

## 签到

- `POST /attendance/check-in`：签到
- `GET /attendance/records`：我的签到记录
- `GET /attendance/today`：今日状态
- `GET /attendance/statistics`：月统计

## 管理端

- `GET /admin/dashboard`：看板
- `GET /admin/users`：用户列表
- `POST /admin/users`：新增用户
- `PUT /admin/users/{id}`：编辑用户
- `DELETE /admin/users/{id}`：禁用用户
- `GET /admin/attendance`：考勤记录
- `GET /admin/rules`：规则列表
- `POST /admin/rules`：创建规则
- `PUT /admin/rules/{id}`：更新规则
- `DELETE /admin/rules/{id}`：删除规则
- `GET /admin/export`：导出 CSV
- `GET /admin/faces`：人脸库列表
- `GET /admin/logs`：操作日志

## 统计

- `GET /statistics/monthly`：月度统计
