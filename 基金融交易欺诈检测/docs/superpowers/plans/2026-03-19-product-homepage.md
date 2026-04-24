# Product Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a formal product-style homepage for the Streamlit site while preserving the existing fraud detection workflows.

**Architecture:** Extract homepage copy and section metadata into a focused content module, then rewrite the Streamlit site to render a product landing experience followed by an interactive workspace. Keep the defense dashboard separate.

**Tech Stack:** Python 3.11, Streamlit, pandas, existing fraud-detection modules, pytest

---

### Task 1: Add homepage content tests first

**Files:**
- Create: `tests/test_site_content.py`
- Create: `src/fraud_detection/site_content.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run `pytest tests/test_site_content.py -q` and confirm failure**
- [ ] **Step 3: Implement minimal homepage content builders**
- [ ] **Step 4: Re-run `pytest tests/test_site_content.py -q` and confirm pass**

### Task 2: Rebuild the Streamlit site homepage

**Files:**
- Modify: `app/site.py`
- Use: `src/fraud_detection/site_content.py`

- [ ] **Step 1: Replace the current function-demo-first layout with a homepage-first layout**
- [ ] **Step 2: Keep single detection, batch detection, and monitoring as a lower-page workspace**
- [ ] **Step 3: Make missing artifacts degrade gracefully**
- [ ] **Step 4: Launch the site locally and verify visual structure**

### Task 3: Verify and document

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add the website launch command**
- [ ] **Step 2: Run full `pytest -q`**
- [ ] **Step 3: Start the website and confirm HTTP 200**
- [ ] **Step 4: Capture the exact URL and report what changed**
