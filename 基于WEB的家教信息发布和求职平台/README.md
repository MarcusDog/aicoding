# 基于 WEB 的家教信息发布和求职平台

本项目根据《基于WEB的家教信息发布和求职平台的设计与实现》任务书实现，面向家长、教员和管理员三类角色，覆盖需求发布、教员认证、接单申请、审核管理、订单生成和统计分析等毕业设计核心内容。

## 目录结构

```text
backend/                 Spring Boot 后端接口
backend/src/main/resources/static/
                         Spring Boot 托管的 Vue 构建产物
frontend/                Vue 前端源码与依赖
analytics/               Python 数据统计模块
tests/                   Python 单元测试
docs/database/           MySQL 数据库脚本
docs/project/            需求、数据库、接口、测试文档
docs/superpowers/plans/  项目实施规划
```

## 技术栈

- 后端：Spring Boot 3、Spring Data JPA、Bean Validation、H2、MySQL
- 前端：Vue 3、Vue Router，由 Spring Boot 托管静态资源
- 数据库：MySQL 8
- 数据分析：Python 3 标准库

## 演示账号

后端启动后会自动写入以下演示账号：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `123456` |
| 家长 | `parent` | `123456` |
| 教员 | `tutor` | `123456` |
| 待认证教员 | `tutor_pending` | `123456` |

## 项目运行

需要 JDK 17+、Maven 3.9+、Node.js 20+。

```bash
cd frontend
npm install
cd ..
./scripts/start_backend.sh
```

浏览器访问：

```text
http://localhost:8080/
```

如只想同步前端静态资源，可运行：

```bash
./scripts/start_frontend.sh
```

默认使用 H2 内存数据库。连接 MySQL 时，先执行 `docs/database/schema.sql`，再运行：

```bash
cd backend
mvn spring-boot:run -Dspring-boot.run.profiles=mysql
```

## Python 统计模块

```bash
python3 analytics/tutor_stats.py
python3 -m unittest discover -s tests
```

## 测试

```bash
cd frontend
npm run check
```

```bash
cd backend
mvn test
```

```bash
python3 -m unittest discover -s tests
```

## 论文写作对应关系

- 第 1 章引言：参考任务书和 `docs/project/需求规格说明书.md` 的项目背景。
- 第 2 章需求分析：使用 `docs/project/需求规格说明书.md`。
- 第 3 章系统设计：使用 `docs/project/数据库设计.md`、接口说明、Vue 路由结构和后端分层结构。
- 第 4 章系统实现：结合 `frontend/` Vue 源码、后端接口、`analytics/` 的关键代码说明。
- 第 5 章系统测试：使用 `docs/project/测试报告.md`。
