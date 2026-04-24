# Product Subpages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the product site into a landing page plus three independent functional pages with shared top navigation.

**Architecture:** Introduce shared page metadata and UI helpers, then move homepage-only content back into the landing page and create dedicated Streamlit pages for single detection, batch detection, and monitoring.

**Tech Stack:** Python 3.11, Streamlit multipage app, pandas, pytest

---

### Task 1: Lock navigation metadata with tests

**Files:**
- Create: `tests/test_site_ui.py`
- Create: `src/fraud_detection/site_ui.py`

- [ ] **Step 1: Write failing tests for page order and metadata**
- [ ] **Step 2: Run `pytest tests/test_site_ui.py -q` and confirm failure**
- [ ] **Step 3: Implement shared page metadata**
- [ ] **Step 4: Re-run tests and confirm pass**

### Task 2: Extract shared UI and runtime helpers

**Files:**
- Create: `src/fraud_detection/site_runtime.py`
- Modify: `src/fraud_detection/__init__.py`

- [ ] **Step 1: Extract shared CSS and top navigation helpers**
- [ ] **Step 2: Extract shared site runtime loader**
- [ ] **Step 3: Verify imports compile**

### Task 3: Split pages

**Files:**
- Modify: `app/site.py`
- Create: `app/pages/1_single_detection.py`
- Create: `app/pages/2_batch_detection.py`
- Create: `app/pages/3_monitoring.py`

- [ ] **Step 1: Reduce homepage to product landing content**
- [ ] **Step 2: Move single detection into its own page**
- [ ] **Step 3: Move batch detection into its own page**
- [ ] **Step 4: Move monitoring into its own page**
- [ ] **Step 5: Verify page compilation**

### Task 4: Verify and document

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update website launch docs**
- [ ] **Step 2: Run full `pytest -q`**
- [ ] **Step 3: Restart the website**
- [ ] **Step 4: Verify navigation in the browser**
