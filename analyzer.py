import os
import pandas as pd
from helper import calculate_total, format_currency
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def load_sales_data(path: str) -> pd.DataFrame:
    """Load sales data from CSV, clean column names, and validate required columns."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File '{path}' not found. Run get_data.py to fetch the sales data."
        )

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    required_cols = {"quantity", "price", "product"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    return df


def save_outputs(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Save cleaned sales data in multiple formats."""
    os.makedirs(output_dir, exist_ok=True)

    df.to_json(f"{output_dir}/sales.json", orient="records", indent=2)
    df.to_excel(f"{output_dir}/sales.xlsx", index=False)
    df.to_csv(f"{output_dir}/sales_cleaned.csv", index=False)

    print("Data saved in multiple formats:")
    print(f"- {output_dir}/sales.json")
    print(f"- {output_dir}/sales.xlsx")
    print(f"- {output_dir}/sales_cleaned.csv")


def calculate_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Add calculated totals using helper functions."""
    df["total"] = df.apply(
        lambda row: calculate_total(row["quantity"], row["price"]), axis=1
    )
    return df


def print_sales_summary(df: pd.DataFrame) -> None:
    """Print formatted sales summary and grand total."""
    print("\nSales Data:")
    for _, row in df.iterrows():
        formatted_total = format_currency(row["total"])
        print(f"{row['product']}: {formatted_total}")

    grand_total = df["total"].sum()
    formatted_grand_total = format_currency(grand_total)
    print(f"\n Grand Total Sales: {formatted_grand_total}")


def get_ai_insights(df: pd.DataFrame, grand_total: float) -> str:
    """Generate AI-powered business insights using OpenAI."""
    # Safety Check: If the dataframe is empty, return early
    if df.empty:
        return " No data available to analyze. Please check your filters."

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Now these lines won't crash
    top_product = df.loc[df["total"].idxmax(), "product"]
    low_product = df.loc[df["total"].idxmin(), "product"]

    # ... rest of your code ...

    prompt = f"""
    Act as a Senior Business Consultant. Analyze these sales metrics:
    - Total Revenue: {grand_total}
    - Best Selling Item: {top_product}
    - Worst Performing Item: {low_product}

    Provide 3 concise, actionable bullet points for the business owner:
    1. A prediction for next month based on the best seller.
    2. A strategic suggestion for the worst performer.
    3. An overall growth tip.
    Format: Use clean Markdown. No fluff.
    """

    try:
        response = client.chat.completions.create(  # fix 2: correct OpenAI syntax
            model="gpt-4o-mini",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content  # fix 3: correct response extraction
    except Exception as e:
        return f" AI Insights unavailable: {e}"


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        df = load_sales_data("data/sales.csv")
        df["total"] = df["quantity"] * df["price"]
        save_outputs(df)

        df = calculate_totals(df)
        print_sales_summary(df)

        grand_total = df["total"].sum()
        insights = get_ai_insights(df, grand_total)
        print("\n AI Insights:\n", insights)

    except Exception as e:
        print(f" Error: {e}")
