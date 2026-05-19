import streamlit as st
import pandas as pd
import plotly.express as px
import os
from analyzer import process_sales_data, get_ai_insights

st.set_page_config(page_title="Fatnicks Stores Intelligence", page_icon="🛍️", layout="wide")

st.title("🛍️ Fatnicks Stores: Sales Intelligence Dashboard")

# ── Data Ingestion ───────────────────────────────────────────────────────────
st.sidebar.header("Data Source")
source = st.sidebar.radio("Select Source", ["Sample Data", "Upload File"])

if source == "Upload File":
    uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = process_sales_data(uploaded)
    else:
        st.info("Please upload a CSV to begin.")
        st.stop()
else:
    df = process_sales_data("output/sales_cleaned.csv")

# ── Date Filtering ───────────────────────────────────────────────────────────
df["date"] = pd.to_datetime(df["date"])
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("Filter by Date", [min_date, max_date])

mask = (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
filtered_df = df.loc[mask]

# ── Executive Metrics ────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"₦{filtered_df['total'].sum():,.0f}")
c2.metric("Total Items", filtered_df["quantity"].sum())
c3.metric("Best Day", filtered_df.groupby("date")["total"].sum().idxmax().strftime("%b %d"))
c4.metric("Worst Day", filtered_df.groupby("date")["total"].sum().idxmin().strftime("%b %d"))

# ── Advanced Visualizations ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Product")
    fig_bar = px.bar(filtered_df.groupby("product")["total"].sum().reset_index(), x="product", y="total", color="product")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Daily Sales Trend")
    fig_line = px.line(filtered_df.groupby("date")["total"].sum().reset_index(), x="date", y="total")
    st.plotly_chart(fig_line, use_container_width=True)

# ── AI Strategic Summary ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🧠 Fatnicks Executive Summary")
if st.button("Generate Full Business Deep-Dive"):
    with st.spinner("Analyzing performance trends..."):
        # We pass the full filtered data for a comprehensive AI review
        report = get_ai_insights(filtered_df)
        st.write(report)

# In app.py
if st.button("Generate Marketing Strategy & Predictions"):
    with st.spinner("Fatnicks Marketing Officer is analyzing performance..."):
        insights = get_ai_insights(filtered_df)
        st.markdown(insights)

# ── Export Features ──────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Export Reports")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download Filtered Data", csv, "fatnicks_report.csv", "text/csv")

if st.sidebar.button("Export Summary to Text"):
    summary_text = f"Fatnicks Stores Summary\nTotal Revenue: {filtered_df['total'].sum()}\nItems Sold: {len(filtered_df)}"
    st.sidebar.download_button("Download Summary", summary_text, "summary.txt")