# Informatica Contractor Onboarding Dashboard

Interactive web dashboard tracking INFA contractor migration status from IQN to SAP Fieldglass, following the Informatica acquisition.

**Live dashboard:** https://nikkimcdonald-dev.github.io/infa-contractors-dashboard/infa_contractors_dashboard.html

## How status is determined

The source workbook (`INFA contractors IQN vs FG (*).xlsx`) has no literal status column — every row shows `Current Phase = Working`. Instead, the file's author color-codes each row. Per the legend supplied by the business owner, status is derived from each row's fill color:

| Color | Status |
|---|---|
| 🟩 Green | Moved to Fieldglass |
| 🟦 Blue | Transition initiated to Fieldglass |
| 🟨 Yellow | Needs clarity from manager |
| 🟧 Orange | Remaining in INFA system |

## Files

- **`prepare_dashboard_data.py`** — reads the source `.xlsx`, classifies each row's status from its Excel fill color, and writes `dashboard_data.json`
- **`dashboard_data.json`** — generated data file consumed by the dashboard
- **`infa_contractors_dashboard.html`** — the interactive dashboard (open in a browser / served via GitHub Pages)
- **`start_dashboard.sh`** — convenience script to serve the dashboard locally

## Regenerating data

When the source workbook is updated:

```bash
cd infa-contractors-dashboard
python3 prepare_dashboard_data.py   # reads ~/Downloads/INFA contractors IQN vs FG (5).xlsx
git add dashboard_data.json
git commit -m "Update contractor data"
git push
```

GitHub Pages serves directly from `main`, so a push updates the live dashboard within a minute or two.

## Running locally

```bash
cd infa-contractors-dashboard
./start_dashboard.sh
```

Opens `http://localhost:8000/infa_contractors_dashboard.html`. A local web server is required — browsers block `fetch()` of local JSON files opened via `file://`.

## Dashboard sections

- **Overview** — doughnut chart of the 4 statuses; top suppliers by status mix; any data-quality issues found in the source file (e.g. broken formulas)
- **By Hiring Manager** — bar chart + sortable table, sorted to surface managers with the most "Needs clarity" contractors first — the actionable follow-up list
- **By Supplier** — status mix per staffing vendor
- **By Department** — status mix per department/cost center
- **Contractor Details** — searchable, filterable table of all 373 contractors; click a name for full details

## Data note

This repo is public and contains contractor names, emails, employee IDs, and managers sourced from an internal HR export. Treat accordingly.
