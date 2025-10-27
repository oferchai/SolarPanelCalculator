#!/usr/bin/env python3
"""
Solar Panel Analysis Dashboard
Interactive Streamlit web application for analyzing solar panel performance and savings
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Solar Panel Analysis Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF8C00;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4CAF50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .highlight-green {
        color: #4CAF50;
        font-weight: bold;
    }
    .highlight-orange {
        color: #FF8C00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process solar panel data"""
    try:
        # Load inverter data
        inverter_df = pd.read_csv('inverter_data_2025-01-01T00_00_00_to_2025-09-30T23_59_59.csv')
        inverter_df['time'] = pd.to_datetime(inverter_df['time'])
        
        # Load pricing data
        prices_df = pd.read_csv('prices_data_2025-01-01T00_00_00_to_2025-09-30T23_59_59.csv')
        prices_df['valid_from'] = pd.to_datetime(prices_df['valid_from'])
        prices_df['valid_to'] = pd.to_datetime(prices_df['valid_to'])
        
        # Merge data
        inverter_df['price_match'] = inverter_df['time'].dt.floor('h')
        prices_df['price_match'] = prices_df['valid_from']
        
        merged_df = inverter_df.merge(
            prices_df[['price_match', 'purchase_price', 'sell_price']], 
            on='price_match', 
            how='left'
        )
        
        # Convert to kWh (10-minute intervals)
        merged_df['consumption_kwh'] = merged_df['consumption'] / 6000
        merged_df['grid_import_kwh'] = merged_df['grid_import'] / 6000
        merged_df['grid_export_kwh'] = merged_df['grid_export'] / 6000
        merged_df['pv_kwh'] = merged_df['pv'] / 6000
        merged_df['battery_charge_kwh'] = merged_df['battery_charge'] / 6000
        merged_df['battery_discharge_kwh'] = merged_df['battery_discharge'] / 6000
        
        # Zero out negative sell prices
        merged_df['sell_price_adjusted'] = merged_df['sell_price'].apply(lambda x: max(x, 0))
        
        # Calculate costs
        merged_df['actual_cost'] = (merged_df['grid_import_kwh'] * merged_df['purchase_price']) - \
                                    (merged_df['grid_export_kwh'] * merged_df['sell_price_adjusted'])
        merged_df['hypothetical_cost'] = merged_df['consumption_kwh'] * merged_df['purchase_price']
        merged_df['savings'] = merged_df['hypothetical_cost'] - merged_df['actual_cost']
        
        # Add time features
        merged_df['month'] = merged_df['time'].dt.to_period('M')
        merged_df['month_name'] = merged_df['time'].dt.strftime('%Y-%m')
        merged_df['date'] = merged_df['time'].dt.date
        merged_df['hour'] = merged_df['time'].dt.hour
        
        return merged_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def calculate_monthly_summary(df):
    """Calculate monthly aggregated metrics"""
    monthly = df.groupby('month_name').agg({
        'consumption_kwh': 'sum',
        'grid_import_kwh': 'sum',
        'grid_export_kwh': 'sum',
        'pv_kwh': 'sum',
        'actual_cost': 'sum',
        'hypothetical_cost': 'sum',
        'savings': 'sum',
        'purchase_price': 'mean'
    }).reset_index()
    
    monthly['self_sufficiency_pct'] = ((monthly['consumption_kwh'] - monthly['grid_import_kwh']) / 
                                        monthly['consumption_kwh'] * 100)
    monthly['savings_rate_pct'] = (monthly['savings'] / monthly['hypothetical_cost'] * 100)
    
    return monthly

def main():
    # Header
    st.markdown('<div class="main-header">☀️ Solar Panel Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    if df is None:
        st.error("Failed to load data. Please ensure CSV files are in the correct location.")
        return
    
    # Sidebar filters
    st.sidebar.header("📊 Filters")
    
    # Date range filter
    # Convert pandas dates to Python datetime.date objects
    import datetime as dt
    
    min_date = pd.Timestamp(df['date'].min()).date() if isinstance(df['date'].min(), pd.Timestamp) else df['date'].min()
    max_date = pd.Timestamp(df['date'].max()).date() if isinstance(df['date'].max(), pd.Timestamp) else df['date'].max()
    
    # Ensure we have proper datetime.date objects
    if not isinstance(min_date, dt.date):
        min_date = dt.date(2024, 12, 31)
    if not isinstance(max_date, dt.date):
        max_date = dt.date(2025, 9, 30)
    
    # Set default start date to 2025-01-01
    default_start_date = dt.date(2025, 1, 1)
    
    st.sidebar.markdown("**Select Date Range:**")
    st.sidebar.info(f"Data available from {min_date} to {max_date}")
    
    # Use format parameter to ensure proper display
    start_date = st.sidebar.date_input(
        "Start Date",
        value=default_start_date,
        min_value=min_date,
        max_value=max_date,
        key="start_date",
        format="YYYY-MM-DD"
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        key="end_date",
        format="YYYY-MM-DD"
    )
    
    # Filter data based on selection
    if start_date and end_date:
        if start_date > end_date:
            st.sidebar.error("Start date must be before end date!")
            filtered_df = df
        else:
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Calculate metrics
    monthly_summary = calculate_monthly_summary(filtered_df)
    
    total_consumption = filtered_df['consumption_kwh'].sum()
    total_grid_import = filtered_df['grid_import_kwh'].sum()
    total_grid_export = filtered_df['grid_export_kwh'].sum()
    total_pv = filtered_df['pv_kwh'].sum()
    total_savings = filtered_df['savings'].sum()
    total_hypothetical = filtered_df['hypothetical_cost'].sum()
    total_actual = filtered_df['actual_cost'].sum()
    savings_rate = (total_savings / total_hypothetical * 100) if total_hypothetical > 0 else 0
    self_sufficiency = ((total_consumption - total_grid_import) / total_consumption * 100) if total_consumption > 0 else 0
    
    # Key Metrics
    st.markdown('<div class="sub-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Savings",
            value=f"{total_savings:,.0f} DKK",
            delta=f"{savings_rate:.1f}% savings rate"
        )
    
    with col2:
        st.metric(
            label="Self-Sufficiency",
            value=f"{self_sufficiency:.1f}%",
            delta=f"{total_consumption - total_grid_import:.0f} kWh self-consumed"
        )
    
    with col3:
        st.metric(
            label="Total PV Generation",
            value=f"{total_pv:,.0f} kWh",
            delta=f"{total_grid_export:,.0f} kWh exported"
        )
    
    with col4:
        st.metric(
            label="Effective Cost",
            value=f"{total_actual/total_consumption:.2f} DKK/kWh" if total_consumption > 0 else "N/A",
            delta=f"-{(total_hypothetical-total_actual)/total_consumption:.2f} DKK/kWh" if total_consumption > 0 else "N/A",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Savings Analysis", "⚡ Energy Flow", "📊 Monthly Breakdown", "🔍 Detailed View"])
    
    with tab1:
        st.markdown('<div class="sub-header">Savings Breakdown</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly savings chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_summary['month_name'],
                y=monthly_summary['savings'],
                name='Monthly Savings',
                marker_color='green'
            ))
            fig.update_layout(
                title="Monthly Savings",
                xaxis_title="Month",
                yaxis_title="Savings (DKK)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Cumulative savings
            cumulative_savings = monthly_summary['savings'].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_summary['month_name'],
                y=cumulative_savings,
                mode='lines+markers',
                name='Cumulative Savings',
                fill='tozeroy',
                marker_color='darkgreen'
            ))
            fig.update_layout(
                title="Cumulative Savings Over Time",
                xaxis_title="Month",
                yaxis_title="Cumulative Savings (DKK)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        # Cost comparison
        st.markdown("### Cost Comparison")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Without Solar", f"{total_hypothetical:,.0f} DKK")
        with col2:
            st.metric("With Solar", f"{total_actual:,.0f} DKK")
        with col3:
            st.metric("Total Savings", f"{total_savings:,.0f} DKK", delta=f"{savings_rate:.1f}%")
    
    with tab2:
        st.markdown('<div class="sub-header">Energy Flow Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly energy flow
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_summary['month_name'],
                y=monthly_summary['consumption_kwh'],
                name='Consumption',
                marker_color='orange'
            ))
            fig.add_trace(go.Bar(
                x=monthly_summary['month_name'],
                y=monthly_summary['grid_import_kwh'],
                name='Grid Import',
                marker_color='red'
            ))
            fig.add_trace(go.Bar(
                x=monthly_summary['month_name'],
                y=monthly_summary['grid_export_kwh'],
                name='Grid Export',
                marker_color='blue'
            ))
            fig.update_layout(
                title="Monthly Energy Flow",
                xaxis_title="Month",
                yaxis_title="Energy (kWh)",
                barmode='group',
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Self-sufficiency rate
            fig = go.Figure()
            colors = ['green' if x > 50 else 'orange' if x > 25 else 'red' 
                     for x in monthly_summary['self_sufficiency_pct']]
            fig.add_trace(go.Bar(
                x=monthly_summary['month_name'],
                y=monthly_summary['self_sufficiency_pct'],
                marker_color=colors,
                name='Self-Sufficiency'
            ))
            fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="50% target")
            fig.update_layout(
                title="Monthly Self-Sufficiency Rate",
                xaxis_title="Month",
                yaxis_title="Self-Sufficiency (%)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        # Daily pattern
        st.markdown("### Daily Energy Pattern (Average by Hour)")
        hourly = filtered_df.groupby('hour')[['pv_kwh', 'consumption_kwh', 'grid_import_kwh', 'grid_export_kwh']].mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hourly.index, y=hourly['pv_kwh']*6, mode='lines', name='PV Generation', line=dict(color='gold', width=3)))
        fig.add_trace(go.Scatter(x=hourly.index, y=hourly['consumption_kwh']*6, mode='lines', name='Consumption', line=dict(color='orange', width=2)))
        fig.add_trace(go.Scatter(x=hourly.index, y=hourly['grid_import_kwh']*6, mode='lines', name='Grid Import', line=dict(color='red', width=2)))
        fig.add_trace(go.Scatter(x=hourly.index, y=hourly['grid_export_kwh']*6, mode='lines', name='Grid Export', line=dict(color='blue', width=2)))
        
        fig.update_layout(
            title="Average Hourly Energy Pattern (Wh/10min)",
            xaxis_title="Hour of Day",
            yaxis_title="Power (Wh)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, width="stretch")
    
    with tab3:
        st.markdown('<div class="sub-header">Monthly Performance</div>', unsafe_allow_html=True)
        
        # Create monthly detail table
        display_df = monthly_summary.copy()
        display_df.columns = ['Month', 'Consumption (kWh)', 'Grid Import (kWh)', 'Grid Export (kWh)', 
                             'PV Generation (kWh)', 'Actual Cost (DKK)', 'Hypothetical Cost (DKK)', 
                             'Savings (DKK)', 'Avg Price (DKK/kWh)', 'Self-Sufficiency (%)', 'Savings Rate (%)']
        
        # Format numeric columns
        for col in display_df.columns[1:]:
            if 'kWh' in col or 'DKK' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.1f}")
            elif '%' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
            elif 'Price' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
        
        st.dataframe(display_df, width="stretch", hide_index=True)
        
        # Download button
        csv = monthly_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Monthly Summary as CSV",
            data=csv,
            file_name=f"solar_monthly_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab4:
        st.markdown('<div class="sub-header">Detailed Analytics</div>', unsafe_allow_html=True)
        
        # Savings sources breakdown
        self_consumed_energy = total_consumption - total_grid_import
        avg_price = filtered_df['purchase_price'].mean()
        self_consumption_value = self_consumed_energy * avg_price
        export_revenue = (filtered_df['grid_export_kwh'] * filtered_df['sell_price_adjusted']).sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for savings sources
            fig = go.Figure(data=[go.Pie(
                labels=['Self-Sufficiency Savings', 'Export Revenue'],
                values=[self_consumption_value, export_revenue],
                marker=dict(colors=['green', 'blue']),
                hole=.3
            )])
            fig.update_layout(title="Savings Sources Breakdown")
            st.plotly_chart(fig, width="stretch")
            
            st.markdown(f"""
            **Savings Breakdown:**
            - Self-Sufficiency: {self_consumption_value:,.2f} DKK ({self_consumption_value/total_savings*100:.1f}%)
            - Export Revenue: {export_revenue:,.2f} DKK ({export_revenue/total_savings*100:.1f}%)
            """)
        
        with col2:
            # Price trends
            daily_avg_price = filtered_df.groupby('date')['purchase_price'].mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_avg_price.index,
                y=daily_avg_price.values,
                mode='lines',
                name='Average Purchase Price',
                line=dict(color='darkblue')
            ))
            fig.update_layout(
                title="Daily Average Grid Purchase Price",
                xaxis_title="Date",
                yaxis_title="Price (DKK/kWh)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        # Export statistics
        st.markdown("### Export Statistics")
        positive_exports = filtered_df[filtered_df['sell_price'] > 0]['grid_export_kwh'].sum()
        negative_exports = filtered_df[filtered_df['sell_price'] <= 0]['grid_export_kwh'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Exported", f"{total_grid_export:,.1f} kWh")
        with col2:
            st.metric("At Positive Prices", f"{positive_exports:,.1f} kWh", 
                     delta=f"{export_revenue:,.2f} DKK revenue")
        with col3:
            st.metric("At Zero/Negative Prices", f"{negative_exports:,.1f} kWh",
                     delta="0.00 DKK revenue")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        Data Period: {df['date'].min()} to {df['date'].max()} | 
        Total Records: {len(filtered_df):,} | 
        Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
