import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Sample Data ---
# This sample dataframe mimics a dataset with product conversion data from social media.
# The last row is used as an example.
df = pd.read_csv('kast_data.csv', index_col=1)
# Assign an index label for the date; here we use the example "9/2/2025"

df = df[df.columns[1:]]
# --- Configuration ---
st.set_page_config(page_title="KAST Dashboard", layout="wide")
st.title("Cumulative Conversions Through Social Media")


# --- Data Cleaning Functions ---
def clean_currency(value):
    """Clean currency values with European format"""
    if isinstance(value, str):
        return float(value.replace('$','').replace('.','').replace(',','.'))
    return value

def clean_decimal(value):
    """Clean decimal values with comma separator"""
    if isinstance(value, str):
        return float(value.replace(',','.'))
    return value

# --- Data Processing ---
# Clean numeric columns
df_clean = df.copy()
df_clean['daily_total_spend'] = df_clean['daily_total_spend'].apply(clean_currency)
df_clean['daily_average_spend'] = df_clean['daily_average_spend'].apply(clean_decimal)

# Calculate cumulative sums
cumulative_cols = ['daily_new_kyc', 'daily_new_card', 'daily_first_spend',
                   'daily_total_spend', 'daily_average_spend']
df_cum = df_clean[cumulative_cols].cumsum().add_prefix('cum_')

# Combine cleaned data with cumulative data
combined_df = pd.concat([df_clean, df_cum], axis=1)

# --- Dashboard Layout ---
st.markdown("""
    This dashboard tracks key conversion metrics with the following features:
    - Automatic currency/number formatting cleanup
    - Cumulative growth visualization
    - Interactive time series analysis
""")


# Key Metrics Summary
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total KYC", f"{combined_df['cum_daily_new_kyc'].iloc[-1]:,}")
with col2:
    st.metric("Total Cards Issued", f"{combined_df['cum_daily_new_card'].iloc[-1]:,}")
with col3:
    st.metric("Total First Spends", f"{combined_df['cum_daily_first_spend'].iloc[-1]:,}")
with col4:
    st.metric("Total Spend", f"${combined_df['cum_daily_total_spend'].iloc[-1]:,.2f}")
with col5:
    st.metric("Avg. Spend/User", f"${combined_df['daily_average_spend'].iloc[-1]:.2f}")

# Cumulative Metrics Visualization
st.subheader("📊 Cumulative Metrics Over Time")
selected_metrics = st.multiselect(
    "Select metrics to display:",
    options=df_cum.columns,
    default=df_cum.columns.tolist()
)

if selected_metrics:
    fig = px.line(
        df_cum.reset_index(),
        x='date',
        y=selected_metrics,
        title="Cumulative Growth Metrics",
        labels={'value': 'Cumulative Value', 'variable': 'Metric'},
        hover_data={'value': ':.2f'},
        height=500
    )
    fig.update_layout(
        hovermode='x unified',
        legend_title_text='Metrics',
        xaxis_title='date',
        yaxis_title='Cumulative Value'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select at least one metric to display.")

# Daily Metrics Comparison
st.subheader("📆 Daily Metrics Breakdown")
metric_choice = st.selectbox(
    "Select daily metric:",
    options=['daily_new_kyc', 'daily_new_card', 'daily_first_spend',
             'daily_total_spend', 'daily_average_spend']
)

fig = px.bar(
    combined_df.reset_index(),
    x='date',
    y=metric_choice,
    title=f"Daily {metric_choice.replace('_', ' ').title()}",
    labels={'value': 'Daily Value'},
    height=400
)
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Value',
    hovermode='x'
)
st.plotly_chart(fig, use_container_width=True)