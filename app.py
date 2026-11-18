import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Predictive Inventory Dashboard", layout="wide")

st.title("📦 Live Predictive Inventory Dashboard")
st.markdown("Automatically syncing data from your cloud Excel file.")

# Direct URL to your raw Excel file on GitHub (or another public cloud host)
# Replace this URL with your actual raw file link
EXCEL_URL = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/orders.xlsx"

@st.cache_data(ttl=600)  # Caches the data for 10 minutes so it re-fetches fresh data automatically
def load_data(url):
    df = pd.read_excel(url, engine='openpyxl')
    return df

try:
    df = load_data(EXCEL_URL)
    
    # Convert order_date column to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    today = datetime.now()

    warnings = []
    item_summary = []

    for name, group in df.groupby('item_name'):
        group = group.sort_values('order_date', ascending=False)
        last_order_date = group.iloc[0]['order_date']
        
        if len(group) > 1:
            total_span = (group.iloc[0]['order_date'] - group.iloc[-1]['order_date']).days
            avg_interval = total_span / (len(group) - 1)
        else:
            avg_interval = 30  # Default fallback cycle
            
        days_elapsed = (today - last_order_date).days
        ratio = days_elapsed / avg_interval
        
        item_summary.append({
            "Item": name,
            "Last Ordered": last_order_date.strftime("%Y-%m-%d"),
            "Days Ago": days_elapsed,
            "Avg Cycle (Days)": round(avg_interval, 1),
            "Cycle Progress": min(1.0, ratio)
        })
        
        if days_elapsed >= (avg_interval * 0.8):
            warnings.append(name)

    # Display Alerts
    st.subheader("⚠️ Top-Up Action Required")
    if not warnings:
        st.success("All stock levels are healthy based on order history!")
    else:
        for item in warnings:
            st.error(f"**TOP UP RECOMMENDED:** {item} is approaching its reorder window.")

    # Display Data Table Summary
    st.subheader("📊 Inventory Velocity Summary")
    summary_df = pd.DataFrame(item_summary)
    st.dataframe(summary_df, use_container_width=True)

except Exception as e:
    st.error(f"Could not load live Excel file. Check your URL path. Error: {e}")