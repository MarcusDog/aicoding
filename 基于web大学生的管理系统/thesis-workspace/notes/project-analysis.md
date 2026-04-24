# Project Analysis

## Basic Information

- Thesis title: 基于Web的大学生志愿者管理系统设计与开发
- Project name: volunteer-management-system
- Task book path: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于web大学生的管理系统\王冠超上海立达学院本科生毕业论文（设计）任务书202410.docx`
- Opening report path: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于web大学生的管理系统\王冠超本科毕业论文(设计)开题报告20241012.docx`
- Project root: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于web大学生的管理系统`
- Student: 王冠超
- Student No.: 202209547
- College: 数字科学学院
- Major: 数据科学与大数据技术
- Supervisor: 朱媛媛

## Project Structure

- Frontend entry:
  - `frontend/src/main.js`
  - `frontend/src/router/index.js`
- Backend entry:
  - `backend/src/main/java/com/lidacollege/volunteer/VolunteerApplication.java`
- Core backend modules:
  - `modules/auth`: 登录、当前用户信息、JWT 认证
  - `modules/admin`: 学生/管理员/活动/公告/签到/时长/报表管理
  - `modules/student`: 活动浏览、报名、签到签退、时长、消息、个人信息
  - `modules/system`: 用户、学生、管理员、公告、消息、日志等基础实体
- Database scripts:
  - `database/schema.sql`
  - `backend/src/main/resources/sql/data.sql`
- Technical stack confirmed in source:
  - Frontend: Vue 3.5.13, Vite 6.2.6, Element Plus 2.9.8, Pinia 3.0.2, Vue Router 4.5.0, Axios 1.8.4, ECharts 5.6.0
  - Backend: Spring Boot 3.4.4, Java 17, MyBatis-Plus 3.5.10.1, JJWT 0.12.6, H2/MySQL

## Key Business Process

1. 管理员维护学生、管理员和活动基础信息。
2. 管理员发布志愿活动，系统自动生成签到码与签退码。
3. 学生浏览活动并提交报名申请。
4. 管理员审核报名，通过后系统预创建签到记录。
5. 学生在规定时间窗口内使用签到码完成签到、签退。
6. 系统据签到结果生成待确认服务时长记录。
7. 管理员确认或撤销服务时长，并同步累计到学生档案。
8. 系统生成公告、消息提醒和统计报表，支持 CSV 导出。

## Evidence Collected

### Screenshots

- `thesis-workspace/screenshots/login-page.png`
- `thesis-workspace/screenshots/admin-dashboard.png`
- `thesis-workspace/screenshots/admin-activity-manage.png`
- `thesis-workspace/screenshots/admin-report.png`
- `thesis-workspace/screenshots/student-home.png`
- `thesis-workspace/screenshots/student-hours.png`
- `thesis-workspace/screenshots/student-messages.png`

### Diagrams and Charts

- `thesis-workspace/charts/system-architecture.png`
- `thesis-workspace/charts/business-flow.png`
- `thesis-workspace/charts/database-er.png`
- `thesis-workspace/charts/monthly-stats.png`

### Candidate Tables

- 角色与功能需求对应表
- 核心数据库表设计表
- 主要测试用例与结果表
- 开发与运行环境配置表

### Core Code Excerpts

- `backend/src/main/java/com/lidacollege/volunteer/modules/auth/service/AuthService.java`
- `backend/src/main/java/com/lidacollege/volunteer/common/security/JwtTokenProvider.java`
- `backend/src/main/java/com/lidacollege/volunteer/modules/admin/service/AdminPortalService.java`
- `backend/src/main/java/com/lidacollege/volunteer/modules/student/service/StudentPortalService.java`
- `database/schema.sql`

### Quantitative Content

- Formula 1: 活动招募完成率
- Formula 2: 学生累计服务时长汇总模型
- Test evidence:
  - 后端 `mvn test` 可执行
  - 前端 `npm run build` 可执行
  - 登录、首页、管理报表等页面与接口已验证

## Constraints and Risks

- 模板文件不是空白模板，而是已完成旧论文，必须保留版式框架并整体替换内容。
- 开题报告中的参考文献条目存在明显失真风险，不能直接复用。
- 部分前端内部页面截图通过浏览器端模拟数据方式采集，论文中应将其作为系统界面展示，不虚构线上运行环境。
- 中文字体、页边距、目录、图题、表题、公式格式必须严格执行上海立达学院规范。
- 需要通过真实官方文档、标准、法规和权威资料补足 12 篇以上可核验参考文献。
