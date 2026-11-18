{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
from datetime import datetime\
import io\
\
st.set_page_config(page_title="Predictive Inventory Dashboard", layout="wide")\
\
st.title("\uc0\u55357 \u56550  Predictive Inventory Top-Up Dashboard")\
st.markdown("Simulating order history and consumption velocity to flag top-up needs automatically.")\
\
# Simulated order history data (or upload your own CSV in the app sidebar)\
default_csv = """item_name,order_date,quantity\
Printer Paper,2026-10-01,10\
Printer Paper,2026-10-20,10\
Cleaning Fluid,2026-09-15,5\
Cleaning Fluid,2026-10-10,5\
Packaging Tape,2026-09-01,20\
Packaging Tape,2026-10-05,20"""\
\
uploaded_file = st.sidebar.file_uploader("Upload your orders.csv", type=["csv"])\
if uploaded_file is not None:\
    df = pd.read_csv(uploaded_file)\
else:\
    df = pd.read_csv(io.StringIO(default_csv))\
\
# Convert columns\
df['order_date'] = pd.to_datetime(df['order_date'])\
today = datetime.now()\
\
warnings = []\
item_summary = []\
\
for name, group in df.groupby('item_name'):\
    group = group.sort_values('order_date', ascending=False)\
    last_order_date = group.iloc[0]['order_date']\
    \
    if len(group) > 1:\
        total_span = (group.iloc[0]['order_date'] - group.iloc[-1]['order_date']).days\
        avg_interval = total_span / (len(group) - 1)\
    else:\
        avg_interval = 30  # Default fallback cycle\
        \
    days_elapsed = (today - last_order_date).days\
    ratio = days_elapsed / avg_interval\
    \
    item_summary.append(\{\
        "Item": name,\
        "Last Ordered": last_order_date.strftime("%Y-%m-%d"),\
        "Days Ago": days_elapsed,\
        "Avg Cycle (Days)": round(avg_interval, 1),\
        "Cycle Progress": min(1.0, ratio)\
    \})\
    \
    if days_elapsed >= (avg_interval * 0.8):\
        warnings.append(name)\
\
# Display Alerts\
st.subheader("\uc0\u9888 \u65039  Top-Up Action Required")\
if not warnings:\
    st.success("All stock levels are healthy based on order history!")\
else:\
    for item in warnings:\
        st.error(f"**TOP UP RECOMMENDED:** \{item\} is approaching its reorder window.")\
\
# Display Data Table Summary\
st.subheader("\uc0\u55357 \u56522  Inventory Velocity Summary")\
summary_df = pd.DataFrame(item_summary)\
st.dataframe(summary_df, use_container_width=True)}