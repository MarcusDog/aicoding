# Tutor Platform Vue Realignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Realign the graduation-design project to the task book by delivering a Spring Boot backend, Vue frontend, MySQL-ready database layer, and Python analytics module in one runnable codebase.

**Architecture:** Keep the existing Spring Boot REST API and business state flow, but replace the current plain static frontend with a Vue 3 router application served by Spring Boot static resources. Preserve H2 for local test convenience, keep MySQL profile and schema for the thesis requirement, and retain Python analytics as a separate module driven by exported business data.

**Tech Stack:** Spring Boot 3, Spring Data JPA, Vue 3, Vue Router, MySQL 8, H2, Python 3.

---

### Task 1: Task Book Alignment

**Files:**
- Modify: `README.md`
- Modify: `docs/project/需求规格说明书.md`
- Modify: `docs/project/测试报告.md`
- Create: `docs/superpowers/plans/2026-04-21-vue-frontend-realignment.md`

- [ ] Summarize the task book constraints into the project docs.
- [ ] Remove outdated wording that says the frontend is plain HTML/JS only.
- [ ] Make the documented architecture explicitly match Spring Boot + Vue + MySQL + Python.

### Task 2: Vue Frontend Reconstruction

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/api.js`
- Create: `frontend/src/helpers.js`
- Create: `frontend/src/store.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/styles.css`
- Modify: `backend/src/main/resources/static/index.html`
- Create: `backend/src/main/resources/static/app/*`
- Create: `backend/src/main/resources/static/vendor/*`
- Delete: `backend/src/main/resources/static/assets/app.js`
- Delete: `backend/src/main/resources/static/assets/styles.css`

- [ ] Rebuild the commercial frontend as a Vue 3 router application.
- [ ] Keep multi-page role flows for login, register, parent, tutor, admin, demand details, and tutor details.
- [ ] Wire the Vue pages to the current REST API and preserve rejected-resubmit business loops.
- [ ] Serve the Vue runtime and router from local static vendor assets instead of a CDN or Vite dev server.

### Task 3: Frontend Delivery Workflow

**Files:**
- Create: `scripts/sync_frontend.sh`
- Modify: `scripts/start_backend.sh`
- Modify: `scripts/start_frontend.sh`
- Modify: `frontend/README.md`

- [ ] Add a repeatable sync step that copies Vue source and vendor runtime files into Spring Boot static resources.
- [ ] Ensure backend startup refreshes the served frontend assets first.
- [ ] Keep the project runnable from the existing backend entry point.

### Task 4: Verification

**Files:**
- Modify: `backend/src/test/java/com/nanhua/tutor/web/StaticFrontendTest.java`
- Test: `backend/src/test/java/com/nanhua/tutor/service/TutorPlatformServiceTest.java`
- Test: `tests/test_tutor_stats.py`

- [ ] Update static frontend tests to assert that Spring Boot serves Vue assets.
- [ ] Verify the backend test suite still passes.
- [ ] Verify the Python analytics test suite still passes.
- [ ] Start the project and confirm the login page and role routing assets are reachable over HTTP.
