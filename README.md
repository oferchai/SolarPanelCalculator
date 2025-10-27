# Solar Panel Capital Savings Analysis

This project analyzes solar panel system performance and calculates capital savings by comparing actual costs with hypothetical grid-only costs.

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

## Usage

1. Set up Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install pandas matplotlib seaborn numpy
   ```

3. Place your data files in the project directory:
   - `inverter_data_*.csv`
   - `prices_data_*.csv`

4. Run the analysis:
   ```bash
   python calculate_savings.py
   ```

## Output Files

- `monthly_savings_summary.csv` - Detailed monthly data
- `solar_savings_analysis.png` - 6 comprehensive charts
- `solar_cost_breakdown.png` - 5 detailed breakdown charts

## Charts Generated

### solar_savings_analysis.png
1. Monthly savings bar chart
2. Cumulative savings over time
3. Total cost comparison (with vs without solar)
4. Monthly energy flow
5. Self-sufficiency rate by month
6. Savings rate by month

### solar_cost_breakdown.png
1. Monthly cost comparison
2. Average grid purchase prices
3. Energy consumption breakdown
4. Savings sources pie chart
5. Monthly breakdown: Self-sufficiency vs export revenue

## License

This project is for personal use and analysis.
