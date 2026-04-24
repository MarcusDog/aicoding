# 当前验证记录

## 已完成

- `frontend` 依赖安装成功
- `backend` 通过 Maven Wrapper 成功编译
- 前端 `npm run build` 成功
- 后端 `mvn test` 成功
- Spring Boot 测试启动通过，H2 数据库初始化成功
- 前端首页 `http://localhost:5173` 返回 `200`
- 管理员真实登录接口验证成功
- 学生真实登录接口验证成功
- 管理员看板接口验证成功
- 学生首页接口验证成功

## 当前已验证命令

```powershell
cd frontend
npm install
npm run build

cd ../backend
.\mvnw.cmd -s .mvn\settings.xml -q -DskipTests compile
.\mvnw.cmd -s .mvn\settings.xml test
```

```powershell
Invoke-WebRequest http://localhost:5173
Invoke-RestMethod http://localhost:8080/api/auth/login
Invoke-RestMethod http://localhost:8080/api/admin/dashboard
Invoke-RestMethod http://localhost:8080/api/student/home
```

## 下一步建议

- 实际启动前后端
- 验证登录、活动管理、报名审核、签到签退、时长认定、报表页面
