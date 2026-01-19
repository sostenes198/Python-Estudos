import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
BUCKET_NAME = "challange-2-pipeline-batch-bovespa-datalake"
AWS_PROFILE = "sostenes-estudos"  # Profile configured in ~/.aws/config
START_DATE = "2024-12-18"
DAYS_TO_FETCH = 3
TICKER_LIST = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'WEGE3.SA']


def extract_data(tickers, start_date_str, days):
    """
    Fetches raw data from Yahoo Finance.
    """
    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
    # yfinance 'end' date is exclusive, so we add days to capture the full range
    end_dt = start_dt + timedelta(days=days)
    end_date_str = end_dt.strftime('%Y-%m-%d')

    print(f"--- 1. EXTRACT: Fetching data from {start_date_str} to {end_date_str} ({days} days) ---")

    try:
        df = yf.download(
            tickers=tickers,
            start=start_date_str,
            end=end_date_str,
            group_by='ticker',
            progress=True
        )
        return df
    except Exception as e:
        print(f"❌ Error connecting to yfinance: {e}")
        return pd.DataFrame()  # Return empty if fails


def transform_data(df_raw):
    """
    Transforms the multi-index DataFrame into a flat table suitable for S3/Athena.
    """
    if df_raw.empty:
        print("❌ No data found. Check if dates are trading days (weekdays).")
        return None

    print("\n--- 2. TRANSFORM: Stacking and formatting ---")

    try:
        # Stack level 0 (Tickers) to move them from columns to rows
        df_clean = df_raw.stack(level=0).reset_index()

        # Standardize the Ticker column name
        cols = df_clean.columns
        if 'level_1' in cols:
            df_clean.rename(columns={'level_1': 'Ticker'}, inplace=True)
        elif 'Ticker' not in cols:
            # Fallback: assume the second column is the Ticker
            df_clean.rename(columns={cols[1]: 'Ticker'}, inplace=True)

        # Create the partition column based on the date
        df_clean['reference_date'] = df_clean['Date'].dt.strftime('%Y-%m-%d')

        print(f"✅ Transformation complete. Total rows: {len(df_clean)}")
        print(df_clean.head())
        return df_clean

    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        return None


def load_to_s3(df_clean, bucket_name, profile):
    """
    Uploads the DataFrame to S3 in Parquet format with Hive-style partitioning.
    """
    if df_clean is None:
        print("⚠️ Skipping Load step due to empty or failed transformation.")
        return

    s3_path = f"s3://{bucket_name}/raw/b3_stocks/"
    print(f"\n--- 3. LOAD: Uploading to {s3_path} ---")
    print(f"ℹ️ Using AWS Profile: {profile}")

    try:
        df_clean.to_parquet(
            s3_path,
            index=False,
            partition_cols=['reference_date'],  # Hive-style partitioning
            compression='snappy',
            storage_options={
                "profile": profile
            }
        )
        print(f"✅ Success! Data saved to S3.")

    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        if "403" in str(e):
            print("HINT: Check if your AWS Role has 'AmazonS3FullAccess' and trust relationships are correct.")


def run_pipeline():
    # 1. Extract
    df_raw = extract_data(TICKER_LIST, START_DATE, DAYS_TO_FETCH)

    # 2. Transform
    df_clean = transform_data(df_raw)

    # 3. Load
    load_to_s3(df_clean, BUCKET_NAME, AWS_PROFILE)


if __name__ == "__main__":
    run_pipeline()