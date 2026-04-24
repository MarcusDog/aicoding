# Homepage Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a formal product homepage that integrates naturally with the existing system showcase pages.

**Architecture:** Keep the current Streamlit application and data service layer, but refactor the page structure so `home` becomes the public product homepage and the existing analysis pages become the integrated showcase experience. Preserve thesis mode, real-data loading, and screenshot/export compatibility.

**Tech Stack:** Python 3.11, Streamlit, Plotly, Pandas, FastAPI, DuckDB

---

### Task 1: Refactor page routing and homepage content

**Files:**
- Modify: `app/streamlit_app.py`
- Test: startup smoke by running `streamlit run app/streamlit_app.py`

- [ ] Add a new `home` page slug and make it the default landing page
- [ ] Replace the current homepage narrative with product-home sections
- [ ] Keep existing analysis pages as downstream showcase pages
- [ ] Preserve thesis query mode compatibility

### Task 2: Rework homepage content blocks

**Files:**
- Modify: `app/streamlit_app.py`

- [ ] Add top navigation and homepage CTA anchors
- [ ] Add hero area with platform-value messaging
- [ ] Add capability cards mapped to report functions
- [ ] Add integrated system preview section
- [ ] Add data-source credibility section

### Task 3: Align system pages with product language

**Files:**
- Modify: `app/streamlit_app.py`

- [ ] Rename page labels to product-oriented wording
- [ ] Make system showcase entry clearer from homepage
- [ ] Keep trend, volatility, correlation, VaR, and source pages intact

### Task 4: Update documentation and run-path guidance

**Files:**
- Modify: `README.md`
- Modify: `docs/system_design.md`
- Modify: `docs/user_manual.md`

- [ ] Document homepage + system integration positioning
- [ ] Keep local startup instructions accurate

### Task 5: Validate end to end

**Files:**
- Modify if needed: `scripts/capture_app_screenshots.py`
- Test: `python -m pytest -q`
- Test: `python scripts/capture_app_screenshots.py`
- Test: local API + Streamlit smoke startup

- [ ] Run tests
- [ ] Start the app and confirm homepage loads
- [ ] Regenerate screenshots
- [ ] Summarize results
