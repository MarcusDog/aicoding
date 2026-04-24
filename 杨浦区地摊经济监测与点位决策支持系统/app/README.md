# Streamlit Frontend Prototype

This folder contains the single-page Streamlit prototype for the Yangpu street-vendor monitoring project.

## Run

From the repository root:

```bash
streamlit run app/main.py
```

## Expected inputs

The app looks for the following files in order:

- `data/processed/predictions.csv`
- `data/processed/features.csv`
- `data/processed/complaints_cleaned.csv`
- `data/raw/candidate_points.csv`

If a file is missing, the app falls back to the next location or to a built-in demo dataset.

## Recommended schemas

`complaints_cleaned.csv`

- `id`
- `created_at`
- `category`
- `content`
- `address`
- `lon`
- `lat`

`candidate_points.csv`

- `point_id`
- `point_name`
- `lon`
- `lat`
- `source`

`features.csv`

- `point_id` or `point_name`
- `date`
- `complaint_count`
- `poi_score`
- `weather_code`
- `holiday_flag`
- `flow_proxy_score`

`predictions.csv`

- `grid_id`
- `score`
- `rank`
- `reason_1`
- `reason_2`
- `risk_level`

## Behavior

- The app shows a heat map, Top 3 recommendations, an explanation chart, filters, and CSV export.
- If all source files are missing, it switches to demo mode and tells you explicitly.
- No other project folders are modified by this frontend prototype.
