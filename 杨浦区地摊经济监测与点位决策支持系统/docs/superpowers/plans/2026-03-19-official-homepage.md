# Official Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Streamlit landing view into a formal operations dashboard homepage for logged-in system users.

**Architecture:** Keep the existing single-page Streamlit app, but split the UI into dashboard sections and top-level module navigation. Reuse current data-loading and recommendation logic so homepage polish does not break the data pipeline.

**Tech Stack:** Python, Streamlit, pandas, folium

---

### Task 1: Add homepage-oriented view helpers

**Files:**
- Modify: `app/main.py`
- Test: `tests/test_pipeline_smoke.py`

- [ ] Add failing tests for homepage metrics and module card metadata.
- [ ] Implement helpers that return homepage metrics and module entries.
- [ ] Run tests and verify the new helpers behave correctly.

### Task 2: Rebuild the top-level page layout

**Files:**
- Modify: `app/main.py`

- [ ] Replace the thesis-style hero and linear layout with a formal dashboard shell.
- [ ] Add top navigation and homepage-first structure.
- [ ] Keep filters, map, Top3, model, evidence, and export flows reachable from navigation.

### Task 3: Validate and launch

**Files:**
- Modify: `README.md`

- [ ] Run `pytest -q`.
- [ ] Run `powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1`.
- [ ] Start Streamlit and verify the homepage loads.
