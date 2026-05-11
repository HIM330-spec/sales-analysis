import streamlit as st
import pandas as pd
import plotly.express as px
import os
from helper import calculate_total, format_currency
from analyzer import get_ai_insights

# 1. Page Config
st.set_page_config(page_title="Sales Representation", layout="wide")

st.title("Sales Representation Dashboard")

# 2. Path Logic
data_path = "output/sales_cleaned.csv"
if not os.path.exists(data_path):
    data_path = "data/sales.csv"

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip().str.lower()

    # Calculate Totals
    df["total"] = df.apply(
        lambda row: calculate_total(row["quantity"], row["price"]), axis=1
    )
    grand_total = df["total"].sum()

    # --- Metrics Row ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(df))
    col2.metric("Grand Total Revenue", format_currency(grand_total))
    col3.metric("Best Seller", df.loc[df["total"].idxmax(), "product"])

    # --- Interactive Filters ---
    st.sidebar.header("Filters")
    product_filter = st.sidebar.multiselect(
        "Filter by Product",
        options=df["product"].unique(),
        default=df["product"].unique(),
    )
    filtered_df = df[df["product"].isin(product_filter)]

    # --- Data Table ---
    st.subheader("Cleaned Sales Data")
    st.dataframe(filtered_df, use_container_width=True)

    # --- Visualizations ---
    st.subheader("Sales Performance")
    chart_type = st.radio("Choose Chart Type:", ["Bar", "Pie"], horizontal=True)

    if chart_type.lower() == "bar":
        st.bar_chart(data=filtered_df, x="product", y="total")

    elif chart_type.lower() == "pie":
        st.subheader("Revenue Share by Product")
        grouped_df = filtered_df.groupby("product", as_index=False)["total"].sum()
        fig = px.pie(
            grouped_df,
            values="total",
            names="product",
            title="Revenue Share by Product",
            hole=0,
        )
        st.plotly_chart(fig)

    # --- AI Insights ---
    st.markdown("---")
    if st.button("Generate AI Business Strategy"):
        with st.spinner("Gemini is analyzing your data..."):
            insights = get_ai_insights(filtered_df, grand_total)
            st.markdown("###Gemini Executive Insights")
            st.info(insights)

    # --- Download Section ---
    st.download_button(
        label="Download Cleaned CSV",
        data=filtered_df.to_csv(index=False),
        file_name="sales_cleaned.csv",
        mime="text/csv",
    )

else:
    st.error(
        f"Data file not found at {data_path}. Please ensure your data folder is set up correctly."
    )
