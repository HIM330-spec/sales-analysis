import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def calculate_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Perform vectorized calculation of totals."""
    df["total"] = df["quantity"] * df["price"]
    return df

def get_ai_insights(df: pd.DataFrame) -> str:
    """Generate Senior Marketing Officer strategy and predictive warnings."""
    if df.empty:
        return "No data available for analysis."

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Aggregated metrics
    total_rev = df["total"].sum()
    top_prod = df.groupby("product")["total"].sum().idxmax()
    worst_prod = df.groupby("product")["total"].sum().idxmin()
    
    # Calculate performance trends
    df_by_date = df.groupby("date")["total"].sum()
    best_day = df_by_date.idxmax().strftime("%Y-%m-%d")
    
    prompt = f"""
    Act as a Senior Marketing Officer for 'Fatnicks Stores'. 
    Data analysis: 
    - Total Revenue: {total_rev}
    - Top Seller: {top_prod}
    - Underperformer: {worst_prod}
    - Peak Sales Day: {best_day}

    Generate a high-impact marketing strategy:
    1. Marketing Capitalization: How do we double down on the Top Seller? (Specific ad/content ideas).
    2. Revitalization Plan: How do we fix the Underperformer? (Bundling, clearance, or rebranding).
    3. Predictive Forecast: Given the Peak Sales Day, what should Fatnicks Stores look out for in the next 14 days?
    4. Risk Warnings: Identify potential inventory or cash flow traps based on current sales velocity.

    Tone: Professional, aggressive growth, analytical. Use clean Markdown.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Marketing Insights unavailable: {e}"

def process_sales_data(file_path: str) -> pd.DataFrame:
    """Load, clean, and prepare the sales ledger."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file {file_path} not found.")
        
    df = pd.read_csv(file_path)
    # Clean column names to prevent mapping errors
    df.columns = df.columns.str.strip().str.lower()
    
    required_cols = {"quantity", "price", "product"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")
    
    return calculate_totals(df)

def save_outputs(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Save cleaned sales data in multiple formats."""
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_json(f"{output_dir}/sales.json", orient="records", indent=2)
    df.to_excel(f"{output_dir}/sales.xlsx", index=False)
    df.to_csv(f"{output_dir}/sales_cleaned.csv", index=False)
    
    print(f"Data saved to {output_dir}/")