# dataset_loader.py
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_all_datasets():
    """
    Loads all mutual fund and historical stock data from the local data folder.
    Returns a dictionary of DataFrames.
    """
    datasets = {}
    
    # 1️⃣ Load Mutual Funds Data
    mf_path = os.path.join(BASE_DIR, "data", "Mutual_Funds.csv")
    if os.path.exists(mf_path):
        datasets['mutual_funds'] = pd.read_csv(mf_path)
        print("✅ Mutual funds data loaded.")
    else:
        print("⚠️ Mutual funds data not found.")
        datasets['mutual_funds'] = pd.DataFrame()
        
    # 2️⃣ Load Historical Stock Data
    stocks_dir = os.path.join(BASE_DIR, "data", "stocks")
    if os.path.exists(stocks_dir):
        all_stock_files = [os.path.join(stocks_dir, f) for f in os.listdir(stocks_dir) if f.endswith('.csv')]
        
        # Filter out empty files before concatenation
        valid_files = [f for f in all_stock_files if os.path.getsize(f) > 0]
        
        if valid_files:
            all_stocks_df = pd.concat([pd.read_csv(f) for f in valid_files], ignore_index=True)
            datasets['nifty_50_historical'] = all_stocks_df
            print(f"✅ Loaded {len(valid_files)} historical stock files.")
        else:
            print("⚠️ No valid stock data files found.")
            datasets['nifty_50_historical'] = pd.DataFrame()
    else:
        print("⚠️ Stocks directory not found.")
        datasets['nifty_50_historical'] = pd.DataFrame()

    return datasets
