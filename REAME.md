#  Sales Intelligence Dashboard

This is a professional data analysis tool built with Python. It takes raw sales data, cleans it, calculates key business metrics, and uses **Google Gemini 3 Flash AI** to generate executive business strategies.

##  Tech Stack
* **Language:** Python 3.x
* **Frontend:** Streamlit (for the interactive dashboard)
* **Data Handling:** Pandas
* **AI Engine:** Google GenAI (Gemini 3 Flash)
* **Environment:** python-dotenv (for security)

## Features
* **Automated Data Cleaning:** Strips whitespace and standardizes column names.
* **Dynamic Metrics:** Calculates Total Revenue and transaction counts on the fly.
* **Interactive Visuals:** Displays sales performance by product using bar charts.
* **AI Consultant:** A dedicated section where Gemini analyzes your "Best" and "Worst" performing products to give actionable growth tips.
* **Export Ready:** Allows users to download the cleaned data as a CSV.

##  How to Run Locally

1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/HIM330-spec/sales-analysis.git](https://github.com/HIM330-spec/sales-analysis.git)
    cd sales-analysis
    ```

2.  **Set up Virtual Environment:**
    ```bash
    python -m venv .venv
    # Activate on Windows:
    .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    * Create a `.env` file in the root folder.
    * Add your key: `GEMINI_API_KEY=your_key_here`

5.  **Launch the App:**
    ```bash
    streamlit run app.py
    ```

## Project Structure
* `app.py`: The main UI/Dashboard script.
* `analyzer.py`: The "Brain" containing data processing and AI logic.
* `helper.py`: Utility functions for currency formatting and calculations.
* `data/`: Folder containing the raw sales CSV.
* `output/`: Where the cleaned data is saved.
