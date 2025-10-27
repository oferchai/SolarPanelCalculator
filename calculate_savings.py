#!/usr/bin/env python3
"""
Solar Panel Capital Savings Analysis
Calculates how much money was saved by having solar panels + battery system
compared to purchasing all energy from the grid at market rates
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

print("Loading data...")
# Load inverter data
inverter_df = pd.read_csv('inverter_data_2025-01-01T00_00_00_to_2025-09-30T23_59_59.csv')
inverter_df['time'] = pd.to_datetime(inverter_df['time'])

# Load pricing data
prices_df = pd.read_csv('prices_data_2025-01-01T00_00_00_to_2025-09-30T23_59_59.csv')
prices_df['valid_from'] = pd.to_datetime(prices_df['valid_from'])
prices_df['valid_to'] = pd.to_datetime(prices_df['valid_to'])

print(f"Loaded {len(inverter_df):,} inverter records and {len(prices_df):,} price records")

# Merge inverter data with prices based on time
# Prices are hourly, inverter data is 10-minute intervals
# Match each inverter record to the price period it falls within
inverter_df['price_match'] = inverter_df['time'].dt.floor('H')
prices_df['price_match'] = prices_df['valid_from']

# Merge the dataframes
merged_df = inverter_df.merge(
    prices_df[['price_match', 'purchase_price', 'sell_price']], 
    on='price_match', 
    how='left'
)

print(f"Merged data: {len(merged_df):,} records")
print(f"Missing price data: {merged_df['purchase_price'].isna().sum()} records")

# Add month column for grouping
merged_df['month'] = merged_df['time'].dt.to_period('M')
merged_df['month_name'] = merged_df['time'].dt.strftime('%Y-%m')

# Convert Wh per 10-minute interval to kWh
# Divide by 6000: 1000 (W to kW) * 6 (10-min intervals per hour)
merged_df['consumption_kwh'] = merged_df['consumption'] / 6000
merged_df['grid_import_kwh'] = merged_df['grid_import'] / 6000
merged_df['grid_export_kwh'] = merged_df['grid_export'] / 6000

# Calculate costs
# Zero out negative sell prices - only count export revenue when price is positive
merged_df['sell_price_adjusted'] = merged_df['sell_price'].apply(lambda x: max(x, 0))

# Actual cost: what was actually paid (grid imports) minus revenue from exports
# When sell_price is negative, we treat export as free (not costing money)
merged_df['actual_cost'] = (merged_df['grid_import_kwh'] * merged_df['purchase_price']) - \
                            (merged_df['grid_export_kwh'] * merged_df['sell_price_adjusted'])

# Hypothetical cost: if all consumption was purchased from grid at the purchase price of that moment
merged_df['hypothetical_cost'] = merged_df['consumption_kwh'] * merged_df['purchase_price']

# Savings per interval
merged_df['savings'] = merged_df['hypothetical_cost'] - merged_df['actual_cost']

# Monthly aggregation
monthly_summary = merged_df.groupby('month_name').agg({
    'consumption_kwh': 'sum',
    'grid_import_kwh': 'sum',
    'grid_export_kwh': 'sum',
    'actual_cost': 'sum',
    'hypothetical_cost': 'sum',
    'savings': 'sum',
    'purchase_price': 'mean'  # Average purchase price for the month
}).reset_index()

monthly_summary['self_sufficiency_pct'] = ((monthly_summary['consumption_kwh'] - monthly_summary['grid_import_kwh']) / 
                                            monthly_summary['consumption_kwh'] * 100)

print(f"\n{'='*100}")
print(f"CAPITAL SAVINGS ANALYSIS")
print(f"{'='*100}")
print(f"\nCurrency: DKK (Danish Krone)")
print(f"\nScenario Comparison:")
print(f"  Hypothetical: All consumption purchased from grid at spot prices")
print(f"  Actual:       With solar panels + battery (grid import - export revenue)")
print(f"  Savings:      Hypothetical cost - Actual cost")

print(f"\n{'='*100}")
print(f"MONTHLY BREAKDOWN WITH SAVINGS SOURCES")
print(f"{'='*100}\n")

# Calculate monthly savings breakdown
monthly_savings_detail = []
for _, row in monthly_summary.iterrows():
    month_name = row['month_name']
    month_data = merged_df[merged_df['month_name'] == month_name]
    
    # Self-consumption savings
    self_consumed = row['consumption_kwh'] - row['grid_import_kwh']
    self_value = self_consumed * row['purchase_price']
    
    # Export revenue
    export_revenue_month = (month_data['grid_export_kwh'] * month_data['sell_price_adjusted']).sum()
    exported_positive = month_data[month_data['sell_price'] > 0]['grid_export_kwh'].sum()
    exported_negative = month_data[month_data['sell_price'] <= 0]['grid_export_kwh'].sum()
    
    monthly_savings_detail.append({
        'month': month_name,
        'self_consumed': self_consumed,
        'self_value': self_value,
        'export_revenue': export_revenue_month,
        'exported_positive': exported_positive,
        'exported_negative': exported_negative
    })
    
    print(f"Month: {row['month_name']}")
    print(f"  Consumption:              {row['consumption_kwh']:>10,.1f} kWh")
    print(f"  Grid Import:              {row['grid_import_kwh']:>10,.1f} kWh ({row['grid_import_kwh']/row['consumption_kwh']*100:>5.1f}% of consumption)")
    print(f"  Grid Export:              {row['grid_export_kwh']:>10,.1f} kWh")
    print(f"  Self-Sufficiency:         {row['self_sufficiency_pct']:>10,.1f}%")
    print(f"  Avg Purchase Price:       {row['purchase_price']:>10,.3f} DKK/kWh")
    print(f"")
    print(f"  Hypothetical Cost:        {row['hypothetical_cost']:>10,.2f} DKK  (if bought all from grid)")
    print(f"  Actual Cost:              {row['actual_cost']:>10,.2f} DKK  (imports - export revenue)")
    print(f"  ")
    print(f"  Savings Breakdown:")
    print(f"    Self-Consumption:       {self_value:>10,.2f} DKK  ({self_consumed:.1f} kWh self-consumed)")
    print(f"    Export Revenue:         {export_revenue_month:>10,.2f} DKK  ({exported_positive:.1f} kWh @ positive prices)")
    if exported_negative > 0:
        print(f"    (Exported @ ≤0 price:   {exported_negative:>10,.1f} kWh - no revenue)")
    print(f"  ───────────────────────────────────")
    print(f"  TOTAL SAVINGS:            {row['savings']:>10,.2f} DKK")
    print(f"  Savings Rate:             {row['savings']/row['hypothetical_cost']*100:>10,.1f}%")
    print(f"")

print(f"{'='*100}")
print(f"TOTAL SUMMARY (Jan - Sep 2025)")
print(f"{'='*100}\n")

total_consumption = monthly_summary['consumption_kwh'].sum()
total_grid_import = monthly_summary['grid_import_kwh'].sum()
total_grid_export = monthly_summary['grid_export_kwh'].sum()
total_hypothetical = monthly_summary['hypothetical_cost'].sum()
total_actual = monthly_summary['actual_cost'].sum()
total_savings = monthly_summary['savings'].sum()
avg_price = monthly_summary['purchase_price'].mean()

print(f"Energy Metrics:")
print(f"  Total Consumption:        {total_consumption:>10,.1f} kWh")
print(f"  Total Grid Import:        {total_grid_import:>10,.1f} kWh ({total_grid_import/total_consumption*100:.1f}% of consumption)")
print(f"  Total Grid Export:        {total_grid_export:>10,.1f} kWh")
print(f"  Self-Generated Energy:    {total_consumption - total_grid_import:>10,.1f} kWh ({(total_consumption - total_grid_import)/total_consumption*100:.1f}%)")
print(f"")
print(f"Financial Metrics:")
print(f"  Average Purchase Price:   {avg_price:>10,.3f} DKK/kWh")
print(f"")
print(f"  Hypothetical Cost:        {total_hypothetical:>10,.2f} DKK")
print(f"    (if all consumption was purchased from grid)")
print(f"")
print(f"  Actual Cost:              {total_actual:>10,.2f} DKK")
print(f"    (grid imports minus export revenue)")
print(f"")
print(f"  TOTAL SAVINGS:            {total_savings:>10,.2f} DKK")
print(f"  Savings Rate:             {total_savings/total_hypothetical*100:>10,.1f}%")
print(f"")
print(f"  Monthly Average Savings:  {total_savings/9:>10,.2f} DKK/month")
print(f"  Projected Annual Savings: {total_savings/9*12:>10,.2f} DKK/year")

print(f"\n{'='*100}")
print(f"SAVINGS BREAKDOWN")
print(f"{'='*100}\n")

# Calculate where savings come from
solar_self_consumption = total_consumption - total_grid_import
value_of_self_consumption = solar_self_consumption * avg_price
export_revenue = (merged_df['grid_export_kwh'] * merged_df['sell_price_adjusted']).sum()
# Count how much was exported at positive vs zero/negative prices
positive_price_exports = merged_df[merged_df['sell_price'] > 0]['grid_export_kwh'].sum()
negative_price_exports = merged_df[merged_df['sell_price'] <= 0]['grid_export_kwh'].sum()

print(f"1. SELF-SUFFICIENCY SAVINGS (Using your own solar instead of buying from grid)")
print(f"   ─────────────────────────────────────────────────────────────────────")
print(f"   Self-Consumed Solar Energy:   {solar_self_consumption:>10,.1f} kWh")
print(f"   Average Grid Price:           {avg_price:>10,.3f} DKK/kWh")
print(f"   Value of Self-Consumption:    {value_of_self_consumption:>10,.2f} DKK")
print(f"   Percentage of Total Savings:  {value_of_self_consumption/total_savings*100:>10,.1f}%")
print(f"")
print(f"2. EXPORT REVENUE (Selling excess solar to the grid)")
print(f"   ─────────────────────────────────────────────────────────────────────")
print(f"   Exported at Positive Prices:  {positive_price_exports:>10,.1f} kWh")
print(f"   Export Revenue Earned:        {export_revenue:>10,.2f} DKK")
print(f"   Average Export Price:         {export_revenue/positive_price_exports if positive_price_exports > 0 else 0:>10,.3f} DKK/kWh")
print(f"   ")
print(f"   Exported at Zero/Neg Prices:  {negative_price_exports:>10,.1f} kWh")
print(f"   Revenue from These Exports:   {0:>10,.2f} DKK (zeroed out)")
print(f"   ")
print(f"   Total Grid Export:            {total_grid_export:>10,.1f} kWh")
print(f"   Total Export Revenue:         {export_revenue:>10,.2f} DKK")
print(f"   Percentage of Total Savings:  {export_revenue/total_savings*100:>10,.1f}%")
print(f"")
print(f"3. TOTAL SAVINGS")
print(f"   ─────────────────────────────────────────────────────────────────────")
print(f"   Self-Consumption Savings:     {value_of_self_consumption:>10,.2f} DKK  ({value_of_self_consumption/total_savings*100:.1f}%)")
print(f"   Export Revenue:               {export_revenue:>10,.2f} DKK  ({export_revenue/total_savings*100:.1f}%)")
print(f"   ═══════════════════════════════════════════════════════════════════")
print(f"   TOTAL SAVINGS:                {total_savings:>10,.2f} DKK  (100.0%)")

# Additional insights
print(f"\n{'='*100}")
print(f"COST PER KWH COMPARISON")
print(f"{'='*100}\n")

effective_cost_per_kwh = total_actual / total_consumption
grid_cost_per_kwh = total_hypothetical / total_consumption

print(f"  Grid-Only Cost:           {grid_cost_per_kwh:>10,.3f} DKK/kWh")
print(f"  Effective Cost with Solar:{effective_cost_per_kwh:>10,.3f} DKK/kWh")
print(f"  Cost Reduction:           {grid_cost_per_kwh - effective_cost_per_kwh:>10,.3f} DKK/kWh ({(grid_cost_per_kwh - effective_cost_per_kwh)/grid_cost_per_kwh*100:.1f}%)")

print(f"\n{'='*100}")

# Export summary to CSV
monthly_summary.to_csv('monthly_savings_summary.csv', index=False)
print(f"\nDetailed monthly data exported to: monthly_savings_summary.csv")

# Create visualizations
print(f"\nGenerating visualizations...")

fig = plt.figure(figsize=(16, 12))

# 1. Monthly Savings Bar Chart
ax1 = plt.subplot(3, 2, 1)
months = monthly_summary['month_name'].str[5:7]  # Extract month number
x_pos = np.arange(len(months))
bars = ax1.bar(x_pos, monthly_summary['savings'], color='green', alpha=0.7, edgecolor='darkgreen')
ax1.set_xlabel('Month')
ax1.set_ylabel('Savings (DKK)')
ax1.set_title('Monthly Savings with Solar System', fontweight='bold', fontsize=12)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(months)
ax1.grid(axis='y', alpha=0.3)
# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, monthly_summary['savings'])):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
             f'{value:.0f}', ha='center', va='bottom', fontsize=9)

# 2. Cumulative Savings Over Time
ax2 = plt.subplot(3, 2, 2)
cumulative_savings = monthly_summary['savings'].cumsum()
ax2.plot(x_pos, cumulative_savings, marker='o', linewidth=2, markersize=8, color='darkgreen')
ax2.fill_between(x_pos, 0, cumulative_savings, alpha=0.3, color='green')
ax2.set_xlabel('Month')
ax2.set_ylabel('Cumulative Savings (DKK)')
ax2.set_title('Cumulative Savings Over Time', fontweight='bold', fontsize=12)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(months)
ax2.grid(True, alpha=0.3)
# Add final value annotation
ax2.text(x_pos[-1], cumulative_savings.iloc[-1], 
         f' {cumulative_savings.iloc[-1]:.0f} DKK', 
         va='center', fontweight='bold', fontsize=10)

# 3. Cost Comparison - Stacked Bar
ax3 = plt.subplot(3, 2, 3)
bar_width = 0.35
x_pos_cost = np.array([0, 1])
actual_costs = [total_actual, 0]
hypothetical_costs = [0, total_hypothetical]
ax3.bar(x_pos_cost, hypothetical_costs, bar_width, label='Without Solar', color='red', alpha=0.7)
ax3.bar(x_pos_cost, actual_costs, bar_width, label='With Solar', color='green', alpha=0.7)
ax3.bar([2], [total_savings], bar_width, label='Total Savings', color='gold', alpha=0.8, edgecolor='orange', linewidth=2)
ax3.set_ylabel('Cost (DKK)')
ax3.set_title('Total Cost Comparison (Jan-Sep 2025)', fontweight='bold', fontsize=12)
ax3.set_xticks([0, 1, 2])
ax3.set_xticklabels(['With Solar', 'Without Solar', 'Savings'])
ax3.legend()
ax3.grid(axis='y', alpha=0.3)
# Add value labels
ax3.text(0, total_actual/2, f'{total_actual:.0f}\nDKK', ha='center', va='center', fontweight='bold', fontsize=10)
ax3.text(1, total_hypothetical/2, f'{total_hypothetical:.0f}\nDKK', ha='center', va='center', fontweight='bold', fontsize=10)
ax3.text(2, total_savings/2, f'{total_savings:.0f}\nDKK', ha='center', va='center', fontweight='bold', fontsize=10)

# 4. Monthly Energy Flow
ax4 = plt.subplot(3, 2, 4)
x_pos_energy = np.arange(len(months))
width = 0.25
ax4.bar(x_pos_energy - width, monthly_summary['consumption_kwh'], width, 
        label='Consumption', color='orange', alpha=0.7)
ax4.bar(x_pos_energy, monthly_summary['grid_import_kwh'], width, 
        label='Grid Import', color='red', alpha=0.7)
ax4.bar(x_pos_energy + width, monthly_summary['grid_export_kwh'], width, 
        label='Grid Export', color='blue', alpha=0.7)
ax4.set_xlabel('Month')
ax4.set_ylabel('Energy (kWh)')
ax4.set_title('Monthly Energy Flow', fontweight='bold', fontsize=12)
ax4.set_xticks(x_pos_energy)
ax4.set_xticklabels(months)
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

# 5. Self-Sufficiency Rate
ax5 = plt.subplot(3, 2, 5)
colors_suffi = ['green' if x > 50 else 'orange' if x > 25 else 'red' 
                for x in monthly_summary['self_sufficiency_pct']]
bars5 = ax5.bar(x_pos, monthly_summary['self_sufficiency_pct'], 
                color=colors_suffi, alpha=0.7, edgecolor='black')
ax5.axhline(y=50, color='green', linestyle='--', linewidth=2, alpha=0.5, label='50% target')
ax5.set_xlabel('Month')
ax5.set_ylabel('Self-Sufficiency (%)')
ax5.set_title('Monthly Self-Sufficiency Rate', fontweight='bold', fontsize=12)
ax5.set_xticks(x_pos)
ax5.set_xticklabels(months)
ax5.set_ylim(0, 100)
ax5.legend()
ax5.grid(axis='y', alpha=0.3)
# Add value labels
for bar, value in zip(bars5, monthly_summary['self_sufficiency_pct']):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
             f'{value:.1f}%', ha='center', va='bottom', fontsize=8)

# 6. Savings Rate by Month
ax6 = plt.subplot(3, 2, 6)
savings_rate = (monthly_summary['savings'] / monthly_summary['hypothetical_cost'] * 100)
bars6 = ax6.bar(x_pos, savings_rate, color='purple', alpha=0.7, edgecolor='darkviolet')
ax6.set_xlabel('Month')
ax6.set_ylabel('Savings Rate (%)')
ax6.set_title('Monthly Savings Rate', fontweight='bold', fontsize=12)
ax6.set_xticks(x_pos)
ax6.set_xticklabels(months)
ax6.grid(axis='y', alpha=0.3)
# Add value labels
for bar, value in zip(bars6, savings_rate):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{value:.1f}%', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('solar_savings_analysis.png', dpi=300, bbox_inches='tight')
print(f"Visualization saved to: solar_savings_analysis.png")

# Create a second figure with detailed cost breakdown
fig2, axes = plt.subplots(2, 3, figsize=(20, 10))

# Plot 1: Monthly cost comparison
ax1 = axes[0, 0]
x_pos_monthly = np.arange(len(months))
width = 0.35
bars1 = ax1.bar(x_pos_monthly - width/2, monthly_summary['hypothetical_cost'], 
                width, label='Without Solar', color='red', alpha=0.6)
bars2 = ax1.bar(x_pos_monthly + width/2, monthly_summary['actual_cost'], 
                width, label='With Solar', color='green', alpha=0.6)
ax1.set_xlabel('Month')
ax1.set_ylabel('Cost (DKK)')
ax1.set_title('Monthly Cost: With vs Without Solar', fontweight='bold', fontsize=12)
ax1.set_xticks(x_pos_monthly)
ax1.set_xticklabels(months)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Average purchase price per month
ax2 = axes[0, 1]
ax2.plot(x_pos_monthly, monthly_summary['purchase_price'], 
         marker='o', linewidth=2, markersize=8, color='darkblue')
ax2.fill_between(x_pos_monthly, 0, monthly_summary['purchase_price'], alpha=0.3, color='blue')
ax2.set_xlabel('Month')
ax2.set_ylabel('Price (DKK/kWh)')
ax2.set_title('Average Grid Purchase Price by Month', fontweight='bold', fontsize=12)
ax2.set_xticks(x_pos_monthly)
ax2.set_xticklabels(months)
ax2.grid(True, alpha=0.3)

# Plot 3: Energy balance (consumption vs grid usage)
ax3 = axes[1, 0]
self_consumed = monthly_summary['consumption_kwh'] - monthly_summary['grid_import_kwh']
x_pos_balance = np.arange(len(months))
ax3.bar(x_pos_balance, self_consumed, label='Self-Consumed Solar', 
        color='green', alpha=0.7)
ax3.bar(x_pos_balance, monthly_summary['grid_import_kwh'], 
        bottom=self_consumed, label='Grid Import', color='red', alpha=0.7)
ax3.set_xlabel('Month')
ax3.set_ylabel('Energy (kWh)')
ax3.set_title('Monthly Consumption Breakdown', fontweight='bold', fontsize=12)
ax3.set_xticks(x_pos_balance)
ax3.set_xticklabels(months)
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# Plot 4: Savings breakdown pie chart
ax4 = axes[1, 1]
solar_self_consumption_total = total_consumption - total_grid_import
value_of_self_consumption_calc = solar_self_consumption_total * avg_price
export_revenue_calc = (merged_df['grid_export_kwh'] * merged_df['sell_price_adjusted']).sum()
# Show savings sources
if export_revenue_calc > 0:
    pie_labels = ['Self-Sufficiency\nSavings', 'Export\nRevenue']
    pie_values = [value_of_self_consumption_calc, export_revenue_calc]
    pie_colors = ['green', 'blue']
else:
    pie_labels = ['Self-Sufficiency\nSavings']
    pie_values = [value_of_self_consumption_calc]
    pie_colors = ['green']

wedges, texts, autotexts = ax4.pie(pie_values, labels=pie_labels, colors=pie_colors, 
                                     autopct='%1.1f%%', startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)
ax4.set_title('Savings Sources Breakdown', fontweight='bold', fontsize=12)

# Plot 5: Monthly breakdown of savings sources
ax5 = axes[1, 2]
monthly_self_consumption = monthly_summary['consumption_kwh'] - monthly_summary['grid_import_kwh']
monthly_self_value = monthly_self_consumption * monthly_summary['purchase_price']
# Calculate monthly export revenue
monthly_export_revenue = []
for month in monthly_summary['month_name']:
    month_data = merged_df[merged_df['month_name'] == month]
    revenue = (month_data['grid_export_kwh'] * month_data['sell_price_adjusted']).sum()
    monthly_export_revenue.append(revenue)
monthly_export_revenue = np.array(monthly_export_revenue)

x_pos_breakdown = np.arange(len(months))
width = 0.35
bars1 = ax5.bar(x_pos_breakdown, monthly_self_value, width, 
                label='Self-Sufficiency Savings', color='green', alpha=0.7)
bars2 = ax5.bar(x_pos_breakdown, monthly_export_revenue, width, bottom=monthly_self_value,
                label='Export Revenue', color='blue', alpha=0.7)
ax5.set_xlabel('Month')
ax5.set_ylabel('Savings (DKK)')
ax5.set_title('Monthly Savings: Self-Sufficiency vs Export Revenue', fontweight='bold', fontsize=12)
ax5.set_xticks(x_pos_breakdown)
ax5.set_xticklabels(months)
ax5.legend()
ax5.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('solar_cost_breakdown.png', dpi=300, bbox_inches='tight')
print(f"Cost breakdown visualization saved to: solar_cost_breakdown.png")

print(f"{'='*100}\n")
