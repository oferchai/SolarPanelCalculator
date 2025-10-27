# Solar Panel Capital Savings Analysis

This project analyzes solar panel system performance and calculates capital savings by comparing actual costs with hypothetical grid-only costs.

## Features

### Interactive Dashboard (Streamlit)
- 📊 Real-time data visualization with Plotly
- 💰 Comprehensive savings analysis
- ⚡ Energy flow monitoring
- 📈 Monthly performance breakdown
- 🔍 Detailed analytics with export statistics
- 📥 Downloadable reports

### Command-Line Analysis
- Detailed console output with monthly breakdowns
- Static chart generation (PNG files)
- CSV export for further analysis

## Overview

The analysis provides detailed insights into:
- **Self-sufficiency savings**: Value of consuming your own solar energy instead of buying from the grid
- **Export revenue**: Income from selling excess solar energy to the grid
- **Monthly breakdowns**: Detailed month-by-month performance metrics
- **Cost comparisons**: Effective cost per kWh with vs without solar

## Data Requirements

The analysis requires two CSV files:
1. **Inverter data**: 10-minute interval measurements including:
   - Consumption, PV generation, battery charge/discharge
   - Grid import/export, state of charge (SOC)
   
2. **Pricing data**: Hourly electricity prices including:
   - Purchase price (import from grid)
   - Sell price (export to grid)

## Key Features

- Accounts for negative export prices (zeroed out when selling price ≤ 0)
- Converts 10-minute interval data correctly (Wh / 6000 = kWh)
- Merges inverter data with hourly pricing data
- Generates comprehensive visualizations
- Exports monthly summary to CSV

## Results Summary

For the period January - September 2025:
- **Total Savings**: 4,543.41 DKK (53.0% savings rate)
- **Self-Sufficiency Savings**: 2,916.98 DKK (64.2%)
- **Export Revenue**: 942.88 DKK (20.8%)
- **Monthly Average**: 504.82 DKK/month
- **Annual Projection**: 6,057.88 DKK/year

## Installation & Usage

### Option 1: Using Poetry (Recommended)

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   cd SolarPanelAnalysis
   poetry install
   ```

3. Run the interactive dashboard:
   ```bash
   poetry run streamlit run app.py
   ```
   The dashboard will open in your browser at `http://localhost:8501`

4. Or run the command-line analysis:
   ```bash
   poetry run python calculate_savings.py
   ```

### Option 2: Using pip/venv

1. Set up Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your data files in the project directory:
   - `inverter_data_*.csv`
   - `prices_data_*.csv`

4. Run the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

5. Or run the command-line analysis:
   ```bash
   python calculate_savings.py
   ```

## Output Files

### Interactive Dashboard
- Real-time interactive charts and metrics
- Filterable date ranges
- Downloadable CSV reports

### Command-Line Analysis
- `monthly_savings_summary.csv` - Detailed monthly data
- `solar_savings_analysis.png` - 6 comprehensive charts
- `solar_cost_breakdown.png` - 5 detailed breakdown charts

## Dashboard Features

### Tabs Overview

1. **💰 Savings Analysis**
   - Monthly and cumulative savings charts
   - Cost comparison visualizations
   - Savings rate trends

2. **⚡ Energy Flow**
   - Monthly energy flow breakdown
   - Self-sufficiency rate tracking
   - Hourly energy patterns

3. **📊 Monthly Breakdown**
   - Detailed monthly performance table
   - Downloadable CSV reports
   - Key metrics comparison

4. **🔍 Detailed View**
   - Savings sources breakdown
   - Price trends analysis
   - Export statistics

## Technology Stack

- **Python 3.9+**
- **Streamlit** - Interactive web dashboard
- **Plotly** - Interactive visualizations
- **Pandas** - Data processing
- **NumPy** - Numerical computations
- **Matplotlib/Seaborn** - Static charts (CLI version)

## Project Structure

```
SolarPanelAnalysis/
├── app.py                  # Streamlit dashboard application
├── calculate_savings.py    # Command-line analysis script
├── pyproject.toml          # Poetry dependency management
├── requirements.txt        # Pip requirements
├── README.md              # This file
├── .gitignore            # Git ignore rules
└── data files (*.csv)    # Your solar panel data
```

## License

This project is for personal use and analysis.

## Contributing

Feel free to open issues or submit pull requests for improvements!

