import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- TEST CONFIGURATION ---
# Choose a date you know had trading (weekday).
# If left empty (""), it defaults to today's date.
TEST_DATE = "2024-12-20"
TICKER_LIST = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'WEGE3.SA']


def extract_data_single_day(tickers, date_str):
    """
    Simulates Airflow's behavior: fetches data for a SPECIFIC day.
    """
    # Logic: Start = Target Date, End = Target Date + 1 Day
    dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
    next_day = (dt_obj + timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"--- 1. EXTRACT: Fetching data from {date_str} to {next_day} ---")

    try:
        df = yf.download(
            tickers=tickers,
            start=date_str,
            end=next_day,
            group_by='ticker',
            progress=True
        )
        return df
    except Exception as e:
        print(f"❌ Error connecting to yfinance: {e}")
        return pd.DataFrame()


def transform_data(df_raw, reference_date):
    """
    Transforms the multi-index DataFrame into a flat table.
    """
    if df_raw.empty:
        print("❌ No data found. The market was likely closed on this date.")
        return None

    print("\n--- 2. TRANSFORM: Stacking and formatting ---")
    print(f"Raw data shape: {df_raw.shape}")

    try:
        # Stack level 0 (Tickers) to move them from columns to rows
        df_clean = df_raw.stack(level=0).reset_index()

        # Standardize the Ticker column name
        cols = df_clean.columns
        if 'level_1' in cols:
            df_clean.rename(columns={'level_1': 'Ticker'}, inplace=True)
        elif 'Ticker' not in cols:
            # Fallback for some pandas versions
            df_clean.rename(columns={cols[1]: 'Ticker'}, inplace=True)

        # Add the reference date (simulating the partition column)
        df_clean['reference_date'] = reference_date

        print(f"✅ Transformation complete. Top 5 rows:")
        print(df_clean.head())
        print(f"Columns: {df_clean.columns.tolist()}")
        return df_clean

    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        print(
            "HINT: If you only downloaded 1 ticker, yfinance does not return a MultiIndex, which breaks .stack(). Keep at least 2 tickers.")
        return None


def save_to_csv(df_clean, date_str):
    """
    Saves to a local CSV file instead of S3.
    """
    if df_clean is None:
        print("⚠️ Skipping Save step due to empty data.")
        return

    filename = f"b3_data_{date_str}.csv"
    print(f"\n--- 3. LOAD (LOCAL): Saving to file ---")

    try:
        df_clean.to_csv(filename, index=False)
        print(f"✅ Success! File saved locally as: {filename}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")


def run_local_test():
    # 1. Determine Date (Simulate {{ ds }})
    if TEST_DATE:
        execution_date = TEST_DATE
    else:
        execution_date = datetime.now().strftime('%Y-%m-%d')

    print(f"🔹 Simulating Airflow Execution for: {execution_date}")

    # 2. Extract
    df_raw = extract_data_single_day(TICKER_LIST, execution_date)

    # 3. Transform
    df_clean = transform_data(df_raw, execution_date)

    # 4. Save Local
    save_to_csv(df_clean, execution_date)


if __name__ == "__main__":
    run_local_test()