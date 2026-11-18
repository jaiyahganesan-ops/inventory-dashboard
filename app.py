import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Live Inventory Dashboard", layout="wide")
st.title("📦 Live Inventory Dashboard (Synced with Google Sheets)")

# Replace this URL with your Published Google Sheet CSV link
SHEET_URL = https://docs.google.com/spreadsheets/d/e/2PACX-1vR63wkMgcNx0Aq8UZJUoFw26AWdhzonlSvXZF3-AWsxCdEMdrm_7Q9NaBNEhyCF6Q/pub?output=csvYOUR_PUBLISHED_GOOGLE_SHEET_CSV_URL_HERE

@st.cache_data(ttl=60) # Refreshes and checks for new data every 60 seconds
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(SHEET_URL)
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
            avg_interval = 30
            
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

    st.subheader("⚠️ Top-Up Action Required")
    if not warnings:
        st.success("All stock levels are healthy based on order history!")
    else:
        for item in warnings:
            st.error(f"**TOP UP RECOMMENDED:** {item} is approaching its reorder window.")

    st.subheader("📊 Inventory Velocity Summary")
    st.dataframe(pd.DataFrame(item_summary), use_container_width=True)

except Exception as e:
    st.error(f"Waiting for valid Google Sheet link... Error: {e}")
