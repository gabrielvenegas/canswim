import yfinance as yf

print("Attempting to download data for S&P 500 (^SPX)...")
try:
    # Get the ticker object
    spx = yf.Ticker("^SPX")

    # Get 1 month of history
    hist = spx.history(period="1mo")

    if not hist.empty:
        print("Success! Data downloaded:")
        print(hist.head())
    else:
        print("Failed: Download returned an empty DataFrame.")

except Exception as e:
    print(f"An error occurred: {e}")
