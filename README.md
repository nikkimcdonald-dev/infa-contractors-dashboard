# INFA Contractors Dashboard

Interactive web dashboard for tracking contractor onboarding progress from the Informatica acquisition to Salesforce.

## Files

- **`prepare_dashboard_data.py`** - Python script that processes the CSV and generates JSON data
- **`dashboard_data.json`** - Generated data file (created after running the script)
- **`infa_contractors_dashboard.html`** - Interactive dashboard (open in browser)
- **`README.md`** - This file

## Quick Start

### 1. Generate Dashboard Data

Run the Python script to process the CSV file:

```bash
cd /Users/nikki.mcdonald/.aisuite/notebook/.agents/artifacts
python3 prepare_dashboard_data.py
```

This will:
- Read the CSV from `~/Downloads/INFA Contractors - Apr Data (1).csv`
- Calculate completion percentages and statistics
- Generate `dashboard_data.json`

### 2. Open Dashboard

**Option A: Using the start script (Recommended)**

Run the provided script which starts a local web server and opens the dashboard:

```bash
cd /Users/nikki.mcdonald/.aisuite/notebook/.agents/artifacts
./start_dashboard.sh
```

The dashboard will open at `http://localhost:8000/infa_contractors_dashboard.html`

Press `Ctrl+C` in the terminal to stop the server when done.

**Option B: Manual web server**

```bash
cd /Users/nikki.mcdonald/.aisuite/notebook/.agents/artifacts
python3 -m http.server 8000
```

Then open your browser and navigate to: `http://localhost:8000/infa_contractors_dashboard.html`

**Why a web server?** Browsers block loading local JSON files for security reasons (CORS policy). Running a local web server solves this issue.

## Dashboard Features

### Summary Cards
- **Total Contractors**: Count of all contractor records
- **Overall Completion**: Percentage of contractors fully onboarded
- **Health Indicator**: Color-coded status (Red/Orange/Yellow/Green)
- **Status Breakdown**: Complete vs. In Progress counts

### Tabs

1. **By Transition Plan & Status**
   - Horizontal bar chart showing completion by transition plan
   - Doughnut chart showing overall status distribution
   - Color-coded health indicators

2. **By Fieldglass Status**
   - Bar chart showing Fieldglass status distribution
   - Note: Most records don't have Fieldglass status yet

3. **Contractor Details**
   - Searchable/filterable table with all contractors
   - Click any contractor name to see full details including Notes

### Interactive Features

- **Search**: Filter contractors by name, department, status, or hiring manager
- **Click to View Details**: Click any contractor name to open a modal with:
  - Full contact information
  - Dates and timeline
  - Current status and transition plan
  - Complete notes with formatting preserved
  
### Health Indicators

The dashboard uses color coding based on completion percentage:
- 🔴 **Red**: < 25% complete
- 🟠 **Orange**: 25-50% complete
- 🟡 **Yellow**: 50-75% complete
- 🟢 **Green**: ≥ 75% complete

## Updating Data

When the CSV file is updated:

1. Run the Python script again to regenerate the JSON:
   ```bash
   python3 prepare_dashboard_data.py
   ```

2. Refresh the dashboard in your browser (press F5 or Cmd+R)

The dashboard will automatically load the new data.

## Completion Calculation

- **Complete**: Only contractors with Status = "Complete" or "Onboarded"
- **In Progress**: All other statuses including blank/empty
- **Binary Model**: Simple complete/incomplete for clearest visibility

## Technical Details

- **No Server Required**: Pure static HTML/CSS/JavaScript
- **Libraries**: Chart.js v4.4.0 (loaded from CDN)
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Mobile Friendly**: Responsive design works on tablets and desktops

## Troubleshooting

**Dashboard shows "Error loading data"**
- Make sure you're running the dashboard through a web server (use `./start_dashboard.sh`)
- Don't open the HTML file directly (double-clicking won't work due to CORS restrictions)
- Make sure `dashboard_data.json` exists in the same directory as the HTML file
- Run `prepare_dashboard_data.py` to generate it if missing

**Charts not showing**
- Check internet connection (Chart.js loads from CDN)
- Try refreshing the page

**Data seems outdated**
- Re-run `prepare_dashboard_data.py` to regenerate from the latest CSV
- Refresh browser after regenerating

## Data Location

- **Source CSV**: `~/Downloads/INFA Contractors - Apr Data (1).csv`
- **Generated JSON**: `.agents/artifacts/dashboard_data.json`
- **Dashboard HTML**: `.agents/artifacts/infa_contractors_dashboard.html`

## Print Support

The dashboard is print-friendly. Use your browser's print function (Cmd+P or Ctrl+P) to print a snapshot of the current view.
