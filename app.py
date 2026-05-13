import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from helper import calculate_total, format_currency
from analyzer import get_ai_insights


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Intelligence", page_icon="🚀", layout="wide")
st.title(" Sales Intelligence Dashboard")


# ── Helpers ───────────────────────────────────────────────────────────────────
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise columns, drop empty rows, coerce numeric types."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.dropna(how="all", inplace=True)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df


def detect_columns(df: pd.DataFrame):
    """
    Detect product, quantity, and price columns even if named differently.
    Returns (product_col, quantity_col, price_col) or raises ValueError.
    """
    product_candidates = ["product", "item", "name", "description", "goods"]
    quantity_candidates = ["quantity", "qty", "units", "count"]
    price_candidates = ["price", "unit_price", "cost", "rate", "value"]

    def find(candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    product_col = find(product_candidates)
    quantity_col = find(quantity_candidates)
    price_col = find(price_candidates)

    missing = []
    if not product_col:
        missing.append("product/item")
    if not quantity_col:
        missing.append("quantity/qty")
    if not price_col:
        missing.append("price/cost")

    if missing:
        raise ValueError(
            f"Could not detect columns for: **{', '.join(missing)}**. "
            f"Columns found: `{', '.join(df.columns)}`"
        )

    return product_col, quantity_col, price_col


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Read CSV, Excel, JSON, or PDF into a DataFrame."""
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    elif name.endswith(".json"):
        data = json.load(uploaded_file)
        return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

    elif name.endswith(".pdf"):
        try:
            import pdfplumber
        except ImportError:
            st.error("PDF support requires `pdfplumber`. Add it to requirements.txt.")
            st.stop()

        tables = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    tables.append(pd.DataFrame(table[1:], columns=table[0]))

        if not tables:
            raise ValueError(
                "No tables detected in this PDF. "
                "Ensure it contains proper table structures, not scanned images."
            )
        return pd.concat(tables, ignore_index=True)

    else:
        raise ValueError(f"Unsupported file type: `{name}`")


# ── Sidebar: Data Source ──────────────────────────────────────────────────────
st.sidebar.header(" Data Source")
source = st.sidebar.radio(
    "Choose data source:", ["Upload your own file", "Use sample data"], index=1
)

df_raw = None

if source == "Upload your own file":
    uploaded = st.sidebar.file_uploader(
        "Upload CSV, Excel, JSON, or PDF", type=["csv", "xlsx", "xls", "json", "pdf"]
    )
    if uploaded:
        try:
            df_raw = load_uploaded_file(uploaded)
            st.sidebar.success(f" Loaded `{uploaded.name}`")
        except Exception as e:
            st.sidebar.error(f"❌ {e}")
            st.stop()
    else:
        st.info("👈 Upload a file from the sidebar to get started.")
        st.stop()

else:
    data_path = "output/sales_cleaned.csv"
    if not os.path.exists(data_path):
        data_path = "data/sales.csv"

    if os.path.exists(data_path):
        df_raw = pd.read_csv(data_path)
    else:
        st.error(" Sample data not found. Run `get_data.py` first or upload a file.")
        st.stop()


# ── Clean & Detect Columns ────────────────────────────────────────────────────
try:
    df = clean_dataframe(df_raw.copy())
    product_col, quantity_col, price_col = detect_columns(df)
except ValueError as e:
    st.error(f" {e}")
    st.stop()

df["total"] = df[quantity_col] * df[price_col]
grand_total = df["total"].sum()


# ── Metrics Row ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric(" Transactions", len(df))
col2.metric(" Total Revenue", format_currency(grand_total))
col3.metric(" Best Seller", df.loc[df["total"].idxmax(), product_col])
col4.metric(" Worst Performer", df.loc[df["total"].idxmin(), product_col])


# ── Sidebar: Filters ──────────────────────────────────────────────────────────
st.sidebar.header(" Filters")
product_filter = st.sidebar.multiselect(
    "Filter by Product",
    options=df[product_col].unique(),
    default=df[product_col].unique(),
)
filtered_df = df[df[product_col].isin(product_filter)]


# ── Data Table ────────────────────────────────────────────────────────────────
st.subheader(" Sales Data")
st.dataframe(filtered_df, use_container_width=True)


# ── Visualizations ────────────────────────────────────────────────────────────
st.subheader(" Sales Performance")
chart_type = st.radio("Choose Chart Type:", ["Bar", "Pie"], horizontal=True)

grouped_df = (
    filtered_df.groupby(product_col)["total"]
    .sum()
    .reset_index()
    .rename(columns={"total": "Revenue"})
)

if chart_type == "Bar":
    fig = px.bar(
        grouped_df,
        x=product_col,
        y="Revenue",
        title="Revenue by Product",
        color=product_col,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    fig = px.pie(
        grouped_df,
        values="Revenue",
        names=product_col,
        title="Revenue Share by Product",
        hole=0.3,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── AI Insights ───────────────────────────────────────────────────────────────
st.markdown("---")
if st.button(" Generate AI Business Strategy"):
    # CHECK: Is the filtered dataframe empty?
    if filtered_df.empty:
        st.warning(
            " Please select at least one product in the sidebar to generate insights."
        )
    else:
        with st.spinner("Analyzing your data..."):
            insights = get_ai_insights(filtered_df, grand_total)
            st.markdown(" AI Executive Insights")
            st.info(insights)


# ── Download ──────────────────────────────────────────────────────────────────
st.download_button(
    label="⬇ Download Cleaned CSV",
    data=filtered_df.to_csv(index=False),
    file_name="sales_cleaned.csv",
    mime="text/csv",
)
