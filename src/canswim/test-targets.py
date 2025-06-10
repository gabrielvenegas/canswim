import pandas as pd
from canswim.targets import Targets
from loguru import logger

def test_load_stock_prices():
    # Create Targets instance
    targets = Targets()

    # Use the public load_data method instead of setting private attributes
    test_tickers = {'AEM', 'AGX', 'APH'}
    start_date = pd.Timestamp('2023-01-01')
    min_samples = 100

    print("=== Testing load_stock_prices() via load_data() ===")
    print(f"Test tickers: {test_tickers}")
    print(f"Start date: {start_date}")
    print(f"Min samples: {min_samples}")

    try:
        # This will call load_stock_prices() internally
        targets.load_data(
            stock_tickers=test_tickers,
            min_samples=min_samples,
            start_date=start_date
        )

        # Check results
        print(f"\n=== Results ===")
        print(f"✅ Success! Stocks loaded: {len(targets.stock_price_dict)}")
        print(f"Stock symbols: {list(targets.stock_price_dict.keys())}")

        # Show details for each loaded stock
        for symbol, data in targets.stock_price_dict.items():
            print(f"\n--- {symbol} ---")
            print(f"Shape: {data.shape}")
            print(f"Date range: {data.index.min()} to {data.index.max()}")
            print(f"Columns: {data.columns.tolist()}")
            print(f"Sample data:\n{data.head(2)}")

        if len(targets.stock_price_dict) == 0:
            print("⚠️  No stocks were loaded - check your data and filters")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")

        # Try to show what we can about the state
        if hasattr(targets, 'stock_price_dict'):
            print(f"Partial results: {len(targets.stock_price_dict)} stocks loaded")

        # Print full traceback for debugging
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_load_stock_prices()
