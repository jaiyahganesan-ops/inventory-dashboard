import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventory Burn-Rate Dashboard", layout="wide")

st.title("📦 Predictive Inventory & Daily Burn-Rate Dashboard")
st.markdown("Tracking inventory consumption velocity and remaining stock based on changing order quantities.")

# Replace with your actual Published Google Sheet CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR63wkMgcNx0Aq8UZJUoFw26AWdhzonlSvXZF3-AWsxCdEMdrm_7Q9NaBNEhyCF6Q/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(SHEET_URL)
    df['order_date'] = pd.to_datetime(df['order_date'])
    today = datetime.now()

    warnings = []
    item_summary = []

    for name, group in df.groupby('item_name'):
        # Sort oldest to newest for historical burn rate calculation
        group = group.sort_values('order_date', ascending=True)
        
        # Get last order details
        last_row = group.iloc[-1]
        last_order_date = last_row['order_date']
        last_qty = last_row['quantity']
        
        days_elapsed = (today - last_order_date).days
        
        if len(group) > 1:
            # Calculate total units consumed between first and second-to-last orders
            # (Excluding the very last order since that's your current stock batch)
            historical_group = group.iloc[:-1]
            total_qty_consumed = historical_group['quantity'].sum()
            
            # Total days span from first order to the last restock date
            first_order_date = group.iloc[0]['order_date']
            total_days = (last_order_date - first_order_date).days
            
            if total_days > 0:
                daily_burn_rate = total_qty_consumed / total_days
            else:
                daily_burn_rate = last_qty / 30  # Fallback
        else:
            # If only 1 order exists in history, assume a default 30-day cycle for that quantity
            daily_burn_rate = last_qty / 30
            
        # Estimate current remaining stock based on daily burn rate
        estimated_units_consumed = days_elapsed * daily_burn_rate
        estimated_remaining_stock = max(0, last_qty - estimated_units_consumed)
        
        # Calculate percentage of stock remaining
        stock_percentage = (estimated_remaining_stock / last_qty) if last_qty > 0 else 0
        
        item_summary.append({
            "Item": name,
            "Last Order Date": last_order_date.strftime("%Y-%m-%d"),
            "Last Qty Ordered": last_qty,
            "Days Since Order": days_elapsed,
            "Daily Burn Rate": round(daily_burn_rate, 2),
            "Est. Remaining Stock": round(estimated_remaining_stock, 1),
            "Stock Level %": round(stock_percentage * 100, 1)
        })
        
        # Trigger warning if stock falls below 20% or days elapsed exceed expected depletion
        if stock_percentage <= 0.20:
            warnings.append(name)

    # Display Alerts
    st.subheader("⚠️ Top-Up Action Required (Stock < 20%)")
    if not warnings:
        st.success("All stock levels are healthy based on consumption burn rates!")
    else:
        for item in warnings:
            st.error(f"**TOP UP RECOMMENDED:** {item} has dropped below its safe stock threshold.")

    # Display Data Table Summary
    st.subheader("📊 Inventory Burn-Rate & Stock Summary")
    summary_df = pd.DataFrame(item_summary)
    st.dataframe(summary_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading or processing inventory data: {e}")
