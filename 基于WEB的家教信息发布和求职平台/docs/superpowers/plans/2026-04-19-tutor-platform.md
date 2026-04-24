# Tutor Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a graduation-design-ready web tutor information publishing and job-seeking platform for parents, tutors, and administrators.

**Architecture:** The system uses a separated frontend/backend structure. The backend is a Spring Boot REST API with MySQL persistence and H2 test support, the frontend is a Vue 3 single page app, and Python provides lightweight platform statistics.

**Tech Stack:** Spring Boot 3, Spring Data JPA, Spring Security-style role modeling, MySQL 8, Vue 3, Vite, Vitest, Python 3.

---

### Task 1: Backend Domain And API

**Files:**
- Create: `backend/pom.xml`
- Create: `backend/src/main/java/com/nanhua/tutor/TutorPlatformApplication.java`
- Create: `backend/src/main/java/com/nanhua/tutor/domain/*.java`
- Create: `backend/src/main/java/com/nanhua/tutor/repository/*.java`
- Create: `backend/src/main/java/com/nanhua/tutor/service/*.java`
- Create: `backend/src/main/java/com/nanhua/tutor/web/*.java`
- Create: `backend/src/test/java/com/nanhua/tutor/service/TutorPlatformServiceTest.java`

- [ ] Write service tests for parent demand publishing, tutor application, admin approval, and dashboard statistics.
- [ ] Implement JPA entities for users, tutor profiles, tutor demands, applications, orders, audit records, and dashboard summaries.
- [ ] Implement service methods with explicit workflow state transitions.
- [ ] Expose REST endpoints for auth demo login, parent operations, tutor operations, admin operations, and dashboard data.
- [ ] Add seed data for demo accounts and sample demands.

### Task 2: Frontend Vue Application

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/api.js`
- Create: `frontend/src/App.test.js`

- [ ] Build a single-page demo interface with role switching for parent, tutor, and admin.
- [ ] Show demand publishing, application submission, admin approval, order status, and statistics panels.
- [ ] Add a restrained product UI visual direction suitable for a graduation defense demo.
- [ ] Add Vitest coverage for core role labels and workflow rendering.

### Task 3: Python Analytics

**Files:**
- Create: `analytics/tutor_stats.py`
- Create: `tests/test_tutor_stats.py`

- [ ] Implement pure Python summary functions for role counts, demand states, application conversion, and recommended operation notes.
- [ ] Add unit tests using the standard `unittest` module.

### Task 4: Database And Documentation

**Files:**
- Create: `docs/database/schema.sql`
- Create: `docs/project/需求规格说明书.md`
- Create: `docs/project/数据库设计.md`
- Create: `docs/project/接口说明.md`
- Create: `docs/project/测试报告.md`
- Create: `README.md`

- [ ] Provide MySQL DDL for all core tables.
- [ ] Document role requirements, business flows, schema design, API endpoints, run instructions, and testing scope.
- [ ] Note environment prerequisites clearly: JDK 17+, Maven 3.9+, Node 20+, Python 3.9+, MySQL 8.

### Task 5: Verification

- [ ] Run Python analytics tests with `python3 -m unittest discover -s tests`.
- [ ] Run frontend install and tests with `npm install` and `npm test -- --run` under `frontend/`.
- [ ] Attempt backend verification with `mvn test` if JDK and Maven are available.
- [ ] Record any environment blockers in the final report.
