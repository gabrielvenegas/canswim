import pandas as pd
from canswim.targets import Targets
import os

def test_load_stock_prices_isolated():
    """Enhanced test with detailed symbol matching debugging"""

    stocks_price_file = "data/data-3rd-party/all_stocks_price_hist_1d.parquet"
    if not os.path.exists(stocks_price_file):
        print(f"❌ Data file not found: {stocks_price_file}")
        return

    print("=== Testing load_stock_prices() with enhanced debugging ===")

    # First, examine the data structure
    print("\n=== Examining data structure ===")
    try:
        df_sample = pd.read_parquet(stocks_price_file, dtype_backend="numpy_nullable")
        print(f"Data shape: {df_sample.shape}")
        print(f"Index: {df_sample.index.names}")
        print(f"Columns: {df_sample.columns}")

        if hasattr(df_sample.index, 'get_level_values'):
            try:
                symbols = df_sample.index.get_level_values('Symbol').unique()
                print(f"Total symbols in file: {len(symbols)}")
                print(f"Sample symbols: {list(symbols[:20])}")

                # Check for common symbol format issues
                print(f"\nSymbol format analysis:")
                print(f"- Any symbols with dots: {any('.' in s for s in symbols[:100])}")
                print(f"- Any symbols with dashes: {any('-' in s for s in symbols[:100])}")
                print(f"- Any symbols with numbers: {any(any(c.isdigit() for c in s) for s in symbols[:100])}")
                print(f"- Symbol length range: {min(len(s) for s in symbols)} to {max(len(s) for s in symbols)}")

                # Store symbols for later comparison
                available_symbols = set(symbols)

            except KeyError as e:
                print(f"❌ Error accessing Symbol level: {e}")
                print(f"Available index levels: {df_sample.index.names}")
                return
        else:
            print("❌ Index is not MultiIndex")
            return

    except Exception as e:
        print(f"❌ Error examining data: {e}")
        return

    print("\n=== Testing symbol matching ===")

    # Test with a few known symbols first
    test_tickers = {'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'}  # Known common symbols

    print(f"Testing with common symbols: {test_tickers}")
    matches = test_tickers.intersection(available_symbols)
    print(f"Matches found: {matches}")

    if not matches:
        print("❌ No matches with common symbols - this suggests a data format issue")
        print("Let's examine symbol formats more closely:")

        # Show actual symbols to help identify format
        sample_symbols = list(available_symbols)[:50]
        print(f"First 50 actual symbols in your data: {sample_symbols}")

        # Check if symbols might have suffixes or prefixes
        for test_symbol in test_tickers:
            potential_matches = [s for s in sample_symbols if test_symbol in s]
            if potential_matches:
                print(f"Potential matches for {test_symbol}: {potential_matches}")

    print("\n=== Testing load_stock_prices() method ===")

    # Create Targets instance
    targets = Targets()

    # Use symbols that we know exist (from our match test above)
    if matches:
        targets._Targets__load_tickers = matches
        print(f"Using matched symbols: {matches}")
    else:
        # Fallback to first few symbols from the actual data
        fallback_symbols = set(list(available_symbols)[:5])
        targets._Targets__load_tickers = fallback_symbols
        print(f"No matches found, using fallback symbols: {fallback_symbols}")

    targets._Targets__start_date = pd.Timestamp('2023-01-01')
    targets.min_samples = 1  # Lower threshold for testing

    # Add debugging to the method by temporarily modifying the matching logic
    print(f"\n=== Running load_stock_prices() ===")

    try:
        # Call the method
        targets.load_stock_prices()

        print(f"✅ Loaded {len(targets.stock_price_dict)} stocks")
        if targets.stock_price_dict:
            for symbol, data in targets.stock_price_dict.items():
                print(f"- {symbol}: {data.shape[0]} rows, dates {data.index.min()} to {data.index.max()}")
        else:
            print("⚠️ No stocks loaded - investigate further")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def debug_symbol_mismatch(your_tickers, data_file):
    """Specific function to debug symbol matching issues"""
    print(f"\n=== Symbol Mismatch Analysis ===")

    # Load your requested tickers (replace this with how you actually load them)
    # your_tickers should be a set/list of the 250 symbols you're trying to load

    df = pd.read_parquet(data_file, dtype_backend="numpy_nullable")
    available_symbols = set(df.index.get_level_values('Symbol').unique())

    print(f"Requested tickers: {len(your_tickers)}")
    print(f"Available symbols in data: {len(available_symbols)}")

    matches = your_tickers.intersection(available_symbols)
    missing = your_tickers - available_symbols

    print(f"Exact matches: {len(matches)}")
    print(f"Missing symbols: {len(missing)}")

    if missing:
        print(f"\nFirst 20 missing symbols: {list(missing)[:20]}")

        # Look for potential matches (fuzzy matching)
        print(f"\nLooking for potential matches:")
        for missing_symbol in list(missing)[:10]:  # Check first 10
            # Look for symbols that contain the missing symbol or vice versa
            potential = [s for s in available_symbols if
                        missing_symbol in s or s in missing_symbol or
                        missing_symbol.replace('.', '') == s or
                        missing_symbol.replace('-', '') == s]
            if potential:
                print(f"  {missing_symbol} -> potential matches: {potential[:5]}")

if __name__ == "__main__":
    test_load_stock_prices_isolated()

    # If you want to debug with your actual 250 tickers:
    # your_250_tickers = set(['AAPL', 'MSFT', ...])  # Your actual ticker list
    # debug_symbol_mismatch(your_250_tickers, "data/data-3rd-party/all_stocks_price_hist_1d.parquet")
