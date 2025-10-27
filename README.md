# Solar Panel Capital Savings Analysis

A comprehensive Python application for analyzing solar panel system performance and calculating capital savings. Features an interactive Streamlit dashboard with real-time data visualization and detailed financial analysis.

## 🎯 Overview

This project provides deep insights into your solar panel system's performance by comparing actual costs with hypothetical grid-only costs. It automatically processes all your solar data files and presents the analysis through an intuitive web interface.

## ✨ Key Features

### Interactive Dashboard (Streamlit)
- 📊 **Real-time Data Visualization** - Interactive Plotly charts with hover tooltips, zoom, and pan
- 💰 **Comprehensive Savings Analysis** - Monthly and cumulative savings tracking
- ⚡ **Energy Flow Monitoring** - Detailed consumption, generation, import/export analysis
- 📈 **Monthly Performance Breakdown** - Tabular view with all key metrics
- 🔍 **Detailed Analytics** - Export statistics, price trends, savings sources breakdown
- 📥 **Downloadable Reports** - Export monthly summary as CSV
- 📁 **Automatic Multi-File Loading** - Loads all `inverter_data*.csv` and `prices_data*.csv` files automatically
- 🔔 **File Processing Notifications** - Shows which files have been loaded successfully
- 📅 **Flexible Date Filtering** - Select custom date ranges for analysis
- 🎨 **Professional UI** - Clean, modern interface with custom styling

### Command-Line Analysis
- Detailed console output with monthly breakdowns
- Static chart generation (PNG files)
- CSV export for further analysis

## 📊 Dashboard Tabs

### 1. 💰 Savings Analysis
- Monthly savings bar chart with values
- Cumulative savings over time
- Cost comparison: with vs without solar
- Savings rate trends

### 2. ⚡ Energy Flow
- Monthly energy flow breakdown (consumption, import, export)
- Self-sufficiency rate tracking with color coding
- Hourly energy pattern analysis (24-hour view)
- Average daily consumption patterns

### 3. 📊 Monthly Breakdown
- Comprehensive monthly performance table
- All metrics formatted for easy reading
- One-click CSV download
- Month-by-month comparison

### 4. 🔍 Detailed View
- Savings sources pie chart (self-sufficiency vs export revenue)
- Daily average grid purchase price trends
- Export statistics with positive/negative price breakdown
- Financial breakdown by category

## 📈 Analysis Results

For the period January - September 2025:
- **Total Savings**: 4,543.41 DKK (53.0% savings rate)
- **Self-Sufficiency**: 38.4% (1,569.2 kWh self-consumed)
- **Self-Sufficiency Savings**: 2,916.98 DKK (64.2% of total savings)
- **Export Revenue**: 942.88 DKK (20.8% of total savings)
- **Monthly Average**: 504.82 DKK/month
- **Annual Projection**: 6,057.88 DKK/year
- **Effective Cost**: 0.987 DKK/kWh (vs 2.100 DKK/kWh grid-only)

## 📋 Data Requirements

Place your CSV files in the project directory. The dashboard will automatically detect and load:

### Inverter Data Files
- Pattern: `inverter_data*.csv`
- Interval: 10-minute measurements
- Required columns:
  - `time` - Timestamp
  - `consumption` - Energy consumption (Wh)
  - `pv` - Solar PV generation (Wh)
  - `grid_import` - Imported from grid (Wh)
  - `grid_export` - Exported to grid (Wh)
  - `battery_charge` - Battery charging (Wh)
  - `battery_discharge` - Battery discharging (Wh)
  - `soc` - State of charge (%)

### Pricing Data Files
- Pattern: `prices_data*.csv`
- Interval: Hourly prices
- Required columns:
  - `valid_from` - Start timestamp
  - `valid_to` - End timestamp
  - `purchase_price` - Import price (DKK/kWh)
  - `sell_price` - Export price (DKK/kWh)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Poetry (for dependency management)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oferchai/SolarPanelCalculator.git
   cd SolarPanelCalculator
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Add your data files:**
   - Copy your `inverter_data*.csv` files to the project directory
   - Copy your `prices_data*.csv` files to the project directory

### Running the Dashboard

#### Option 1: Using the Launch Script (Easiest)
```bash
./RUN_DASHBOARD.sh
```

#### Option 2: Direct Command
```bash
poetry run streamlit run app.py
```

#### Option 3: Interactive Shell
```bash
poetry shell
streamlit run app.py
```

The dashboard will automatically:
- Start up in a few seconds
- Open in your browser at **http://localhost:8501**
- Load all matching CSV files
- Display file processing status
- Present your solar panel data with interactive charts

### Running Command-Line Analysis
```bash
poetry run python calculate_savings.py
```

### Stopping the Dashboard
Press `Ctrl+C` in the terminal where the dashboard is running.

## 🔧 Key Technical Features

### Smart Data Processing
- **Automatic file discovery** - No need to specify filenames
- **Multi-file support** - Combines data from multiple time periods
- **Chronological sorting** - Data automatically sorted by timestamp
- **Error handling** - Graceful handling of missing or malformed files
- **Data caching** - Fast reload with Streamlit's @st.cache_data

### Accurate Calculations
- **10-minute interval correction** - Properly converts Wh to kWh (÷6000)
- **Negative price handling** - Zeros out negative export prices
- **Time-matched pricing** - Hourly prices matched to 10-minute data
- **Real-time cost calculation** - Actual vs hypothetical cost comparison

### Financial Metrics
- Self-sufficiency savings (solar consumption vs grid purchase)
- Export revenue (only positive price periods counted)
- Cost per kWh comparison (effective vs grid-only)
- Monthly and cumulative savings tracking
- Savings rate percentage calculation

## 📁 Project Structure

```
SolarPanelAnalysis/
├── app.py                      # Streamlit dashboard (main application)
├── calculate_savings.py        # Command-line analysis script
├── RUN_DASHBOARD.sh           # Launcher script
├── pyproject.toml             # Poetry dependency configuration
├── poetry.lock                # Locked dependency versions
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
└── data files/                # Your CSV files (not tracked in git)
    ├── inverter_data*.csv
    └── prices_data*.csv
```

## 🛠️ Technology Stack

- **Python 3.9+** - Core programming language
- **Poetry** - Dependency management and packaging
- **Streamlit 1.50+** - Interactive web dashboard framework
- **Plotly 6.3+** - Interactive visualizations
- **Pandas 2.3+** - Data processing and analysis
- **NumPy 2.3+** - Numerical computations
- **Matplotlib 3.9+** - Static charts (CLI version)
- **Seaborn 0.13+** - Statistical visualizations (CLI version)

## 📖 Usage Tips

### Date Range Selection
- Default view shows 2025-01-01 to 2025-09-30
- Use sidebar date pickers to customize range
- Both start and end dates are inclusive
- Data outside available range is automatically filtered

### File Management
- Click "📁 Loaded Data Files" to see which files were processed
- Add new files anytime - just refresh the dashboard
- Files are loaded in alphabetical order
- Multiple files are combined automatically

### Downloading Reports
- Navigate to "📊 Monthly Breakdown" tab
- Click "📥 Download Monthly Summary as CSV" button
- File includes all monthly metrics for further analysis

### Performance
- First load caches data for faster subsequent loads
- Filter by date range for focused analysis
- All charts are interactive - hover for details

## 🔑 Key Insights

The dashboard helps you understand:
- How much money solar panels save you each month
- What percentage of your consumption is self-generated
- How export prices affect your revenue
- When you consume the most energy (hourly patterns)
- Whether your system performance is improving
- Return on investment timeline

## 🤝 Contributing

Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests for improvements
- Share your experience and suggestions
- Star the repository if you find it useful!

## 📝 License

This project is for personal use and analysis.

## 🙏 Acknowledgments

Built with ❤️ for solar panel owners who want to understand and optimize their energy usage and savings.

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/oferchai/SolarPanelCalculator/issues)
