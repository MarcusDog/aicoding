# Volunteer Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a graduation-project-ready volunteer management system with student and admin portals, complete business flow, local deployment, seed data, and test coverage.

**Architecture:** Use a front-end/back-end separated B/S architecture. The backend provides JWT-authenticated REST APIs, file upload endpoints, business workflows, and reporting services over MySQL. The frontend uses Vue 3 and Element Plus to implement separate student/admin flows on top of a shared login and routing shell.

**Tech Stack:** Vue 3, Vite, Element Plus, Pinia, Vue Router, Axios, ECharts, Spring Boot, MyBatis-Plus, MySQL 8, Maven, JWT, JUnit 5

---

## File Structure

### Root

- Create: `frontend/`
- Create: `backend/`
- Create: `database/`
- Create: `uploads/`
- Create: `scripts/`
- Create: `docs/implementation/`

### Frontend

- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/api/http.js`
- Create: `frontend/src/api/modules/*.js`
- Create: `frontend/src/layouts/AdminLayout.vue`
- Create: `frontend/src/layouts/StudentLayout.vue`
- Create: `frontend/src/views/auth/LoginView.vue`
- Create: `frontend/src/views/student/*.vue`
- Create: `frontend/src/views/admin/*.vue`
- Create: `frontend/src/components/*.vue`
- Create: `frontend/src/styles/*.css`

### Backend

- Create: `backend/pom.xml`
- Create: `backend/src/main/resources/application.yml`
- Create: `backend/src/main/resources/application-dev.yml`
- Create: `backend/src/main/resources/mapper/`
- Create: `backend/src/main/java/com/lidacollege/volunteer/VolunteerApplication.java`
- Create: `backend/src/main/java/com/lidacollege/volunteer/common/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/config/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/auth/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/student/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/admin/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/activity/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/signup/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/sign/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/hours/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/notice/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/report/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/file/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/log/**`
- Create: `backend/src/test/java/com/lidacollege/volunteer/**`

### Database and Scripts

- Create: `database/schema.sql`
- Create: `database/seed.sql`
- Create: `scripts/start-backend.ps1`
- Create: `scripts/start-frontend.ps1`
- Create: `scripts/init-db.ps1`

## Task 1: Scaffold Project Structure

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `backend/pom.xml`
- Create: `backend/src/main/resources/application.yml`
- Create: `backend/src/main/java/com/lidacollege/volunteer/VolunteerApplication.java`

- [ ] **Step 1: Create the directory skeleton**

Create the root folders and source folders listed above.

- [ ] **Step 2: Write frontend dependency manifest**

Add Vue, Element Plus, Pinia, Vue Router, Axios, ECharts, and Vite scripts.

- [ ] **Step 3: Write backend Maven manifest**

Add Spring Boot Web, Validation, MyBatis-Plus, MySQL driver, JWT utilities, Lombok, and Spring Boot Test.

- [ ] **Step 4: Add minimal boot files**

Create `frontend/src/main.js`, `frontend/src/App.vue`, and the Spring Boot application entry point.

- [ ] **Step 5: Verify both toolchains can install and compile**

Run:

```powershell
cd frontend; npm install
cd ../backend; mvn -q -DskipTests compile
```

Expected:

- Frontend dependencies install successfully
- Backend compiles without tests

## Task 2: Build Database Schema and Seed Data

**Files:**
- Create: `database/schema.sql`
- Create: `database/seed.sql`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/**/entity/*.java`
- Test: `backend/src/test/java/com/lidacollege/volunteer/schema/SchemaSmokeTest.java`

- [ ] **Step 1: Translate the approved spec into SQL DDL**

Create all tables, unique constraints, foreign keys, indexes, default values, and enum-like varchar fields.

- [ ] **Step 2: Write seed data**

Insert:

- 2 admin accounts
- 80 to 120 students
- 6 to 8 activity categories
- 20 to 30 activities
- signups, signs, hours, notices, and messages with internally consistent states

- [ ] **Step 3: Mirror schema in entity classes**

Create Java entity classes aligned with the SQL schema.

- [ ] **Step 4: Add schema smoke test**

Write a test that verifies the schema files exist and contain all required core tables.

- [ ] **Step 5: Verify SQL scripts are loadable**

Run:

```powershell
Get-Content database/schema.sql | Select-Object -First 20
Get-Content database/seed.sql | Select-Object -First 20
```

Expected:

- Core table definitions and insert blocks are present

## Task 3: Implement Backend Foundations

**Files:**
- Create: `backend/src/main/java/com/lidacollege/volunteer/common/api/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/common/exception/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/config/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/auth/**`
- Test: `backend/src/test/java/com/lidacollege/volunteer/auth/AuthControllerTest.java`

- [ ] **Step 1: Add unified API response and global exception handling**

Implement success/error wrappers and validation/error translation.

- [ ] **Step 2: Add JWT authentication**

Implement login request, token generation, token parsing, and request filtering/interception.

- [ ] **Step 3: Add current-user context and role checks**

Ensure student and admin endpoints can be protected.

- [ ] **Step 4: Add login API**

Support username/password login and return profile basics plus token.

- [ ] **Step 5: Write and run backend auth tests**

Run:

```powershell
cd backend; mvn -q -Dtest=AuthControllerTest test
```

Expected:

- Authentication tests pass

## Task 4: Implement Core Backend Business Modules

**Files:**
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/student/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/activity/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/signup/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/sign/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/hours/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/notice/**`
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/report/**`
- Test: `backend/src/test/java/com/lidacollege/volunteer/modules/**`

- [ ] **Step 1: Implement student profile and dashboard APIs**

Support current profile, update profile, home summary, notices, hours summary.

- [ ] **Step 2: Implement activity APIs**

Support admin CRUD, student list/detail, publish/cancel/update rules.

- [ ] **Step 3: Implement signup workflow**

Support apply, cancel, review approve/reject, capacity validation, and message creation.

- [ ] **Step 4: Implement sign-in/out workflow**

Support code-based sign-in/out, admin fix flow, absent marking, and sign record rules.

- [ ] **Step 5: Implement hours workflow**

Support generation, confirm, adjust, revoke, and student total recomputation.

- [ ] **Step 6: Implement notice, report, export, and operation log APIs**

Support public notices, personal messages, dashboard charts, list reports, and Excel export.

- [ ] **Step 7: Run backend module tests**

Run:

```powershell
cd backend; mvn test
```

Expected:

- Module tests pass

## Task 5: Implement File Upload and Local Runtime Scripts

**Files:**
- Create: `backend/src/main/java/com/lidacollege/volunteer/modules/file/**`
- Create: `scripts/init-db.ps1`
- Create: `scripts/start-backend.ps1`
- Create: `scripts/start-frontend.ps1`
- Modify: `backend/src/main/resources/application-dev.yml`

- [ ] **Step 1: Implement upload endpoints**

Support activity cover, activity attachment, notice attachment, and avatar upload.

- [ ] **Step 2: Configure local upload path**

Store files under root `uploads/` and expose them for local preview.

- [ ] **Step 3: Add local startup scripts**

Create scripts for DB initialization, backend startup, and frontend startup.

- [ ] **Step 4: Verify local scripts are readable and point to correct paths**

Run:

```powershell
Get-Content scripts/init-db.ps1
Get-Content scripts/start-backend.ps1
Get-Content scripts/start-frontend.ps1
```

Expected:

- Scripts reference the current workspace paths

## Task 6: Build Frontend Shell, Routing, and Auth

**Files:**
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/api/http.js`
- Create: `frontend/src/views/auth/LoginView.vue`
- Create: `frontend/src/layouts/AdminLayout.vue`
- Create: `frontend/src/layouts/StudentLayout.vue`
- Test: `frontend` smoke run

- [ ] **Step 1: Configure router, auth store, and HTTP client**

Add token persistence, request interceptors, and role-aware route guards.

- [ ] **Step 2: Build login view**

Support admin/student login and redirect by role.

- [ ] **Step 3: Build shared admin and student layouts**

Add header, sidebar, breadcrumb/title area, and logout.

- [ ] **Step 4: Verify frontend dev server starts**

Run:

```powershell
cd frontend; npm run build
```

Expected:

- Frontend compiles successfully

## Task 7: Build Student Portal Pages

**Files:**
- Create: `frontend/src/views/student/StudentHomeView.vue`
- Create: `frontend/src/views/student/ActivityListView.vue`
- Create: `frontend/src/views/student/ActivityDetailView.vue`
- Create: `frontend/src/views/student/MySignupView.vue`
- Create: `frontend/src/views/student/CheckinView.vue`
- Create: `frontend/src/views/student/MyHoursView.vue`
- Create: `frontend/src/views/student/MyMessagesView.vue`
- Create: `frontend/src/views/student/ProfileView.vue`
- Create: `frontend/src/api/modules/student.js`
- Create: `frontend/src/api/modules/activity.js`

- [ ] **Step 1: Build student home and activity browsing**

- [ ] **Step 2: Build signup and cancel flow**

- [ ] **Step 3: Build sign-in/out page**

- [ ] **Step 4: Build hours, messages, and profile pages**

- [ ] **Step 5: Verify frontend build after student pages**

Run:

```powershell
cd frontend; npm run build
```

Expected:

- Build succeeds

## Task 8: Build Admin Portal Pages

**Files:**
- Create: `frontend/src/views/admin/AdminDashboardView.vue`
- Create: `frontend/src/views/admin/StudentManageView.vue`
- Create: `frontend/src/views/admin/ActivityManageView.vue`
- Create: `frontend/src/views/admin/SignupReviewView.vue`
- Create: `frontend/src/views/admin/SignManageView.vue`
- Create: `frontend/src/views/admin/HoursManageView.vue`
- Create: `frontend/src/views/admin/NoticeManageView.vue`
- Create: `frontend/src/views/admin/ReportView.vue`
- Create: `frontend/src/views/admin/AdminManageView.vue`
- Create: `frontend/src/api/modules/admin.js`
- Create: `frontend/src/api/modules/report.js`

- [ ] **Step 1: Build admin dashboard and chart panels**

- [ ] **Step 2: Build student and admin management pages**

- [ ] **Step 3: Build activity, signup review, sign, and hours management pages**

- [ ] **Step 4: Build notice, report, and export pages**

- [ ] **Step 5: Verify frontend build after admin pages**

Run:

```powershell
cd frontend; npm run build
```

Expected:

- Build succeeds

## Task 9: End-to-End Verification and Local Deployment

**Files:**
- Create: `docs/implementation/local-runbook.md`
- Create: `docs/implementation/test-report.md`
- Modify: `scripts/*.ps1`

- [ ] **Step 1: Write local runbook**

Document MySQL setup, script execution, frontend/backend startup, and default accounts.

- [ ] **Step 2: Execute full verification**

Verify:

- admin login
- student login
- activity publish
- signup
- review
- sign in/out
- hours confirmation
- report view
- export

- [ ] **Step 3: Record issues and fix blockers**

- [ ] **Step 4: Write concise test report**

- [ ] **Step 5: Re-run final backend and frontend verification**

Run:

```powershell
cd backend; mvn test
cd ../frontend; npm run build
```

Expected:

- Backend tests pass
- Frontend build succeeds
