from typing import Union
from loguru import logger
from darts.dataprocessing.transformers import MissingValuesFiller
from darts import TimeSeries
import pandas as pd


class Targets:
    def __init__(self) -> None:
        self.target_series = {}

    def load_data(
        self,
        stock_tickers: set = None,
        min_samples: int = -1,
        start_date: pd.Timestamp = None,
    ):
        self.__start_date = start_date
        self.__load_tickers = stock_tickers
        self.min_samples = min_samples
        self.load_stock_prices()

    @property
    def pyarrow_filters(self):
        return [
            ("Symbol", "in", self.__load_tickers),
            ("Date", ">=", self.__start_date),
        ]

    def load_stock_prices(self):
        stocks_price_file = "data/data-3rd-party/all_stocks_price_hist_1d.parquet"
        logger.info(f"Loading data from: {stocks_price_file}")

        try:
            # Load the full parquet file (PyArrow filters don't work with MultiIndex)
            stocks_df = pd.read_parquet(
                stocks_price_file,
                dtype_backend="numpy_nullable",
            )

            logger.info("Raw data loaded")

            # Filter by symbols
            available_symbols = stocks_df.index.get_level_values('Symbol').unique()
            valid_tickers = [t for t in self.__load_tickers if t in available_symbols]

            logger.info(f"Available tickers in stocks DataFrame: {len(valid_tickers)}")

            if valid_tickers:
                stocks_df = stocks_df.loc[valid_tickers]
                logger.info(f"Filtered to {len(valid_tickers)} symbols: {valid_tickers}")
            else:
               logger.warning(f"No matching symbols found. Available: {list(available_symbols[:10])}...")
               self.stock_price_dict = {}
               return

            # Filter by date
            if self.__start_date is not None:
                stocks_df = stocks_df.loc[
                    stocks_df.index.get_level_values('Date') >= self.__start_date
                ]

                logger.info(f"Filtered by start date: {self.__start_date}")

            logger.info("Filtered data loaded")

            # Filter by essential columns
            essential_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            stocks_df = stocks_df.dropna(subset=essential_cols)

            # Safely flatten the column MultiIndex if it exists
            if isinstance(stocks_df.columns, pd.MultiIndex) and stocks_df.columns.nlevels > 1:
                logger.info(f"Flattening MultiIndex columns with {stocks_df.columns.nlevels} levels")
                stocks_df.columns = stocks_df.columns.droplevel(0)  # Remove 'Price' level
            else:
                logger.info("Columns already flattened or not MultiIndex")

            logger.info(f"Final columns: {stocks_df.columns.tolist()}")

            # Process individual stocks
            stock_price_dict = {}
            tickers = list(stocks_df.index.get_level_values('Symbol').unique())
            logger.info(f"Price history loaded for {len(tickers)} stocks: {tickers}")

            for t in tickers:
                logger.info(f"Validating price data for {t}")
                try:
                    stock_full_hist = stocks_df.loc[t]

                    if len(stock_full_hist.index) >= self.min_samples:
                        # Ensure index is datetime
                        stock_full_hist.index = pd.to_datetime(stock_full_hist.index)

                        # Drop Adj Close if it exists
                        # Ref: https://help.yahoo.com/kb/adjusted-close-sln28256.html
                        if "Adj Close" in stock_full_hist.columns:
                            stock_full_hist = stock_full_hist.drop(columns=["Adj Close"])
                            logger.info(f"Dropped Adj Close column for {t}")

                        stock_price_dict[t] = stock_full_hist
                        logger.info(f"Added ticker: {t} with {len(stock_full_hist)} samples")
                    else:
                        logger.info(
                            f"Skipping {t} from price series. Not enough samples "
                            f"({len(stock_full_hist.index)} < {self.min_samples})"
                        )
                except Exception as e:
                    logger.error(f"Error processing ticker {t}: {e}")
                    continue

            self.stock_price_dict = stock_price_dict
            logger.info(f"Successfully loaded {len(stock_price_dict)} stocks")

        except Exception as e:
            logger.error(f"Error loading stock prices: {e}")
            self.stock_price_dict = {}
            raise

    def prepare_data(
        self, stock_price_series: dict = None, target_columns: Union[str, list] = None
    ):
        def drop_non_target_columns(series):
            cols = series.columns
            non_target_columns = list(set(cols) - set(target_columns))
            new_series = series.drop_columns(col_names=non_target_columns)
            # logger.info(f'dropped non-target columns: {non_target_columns}')
            return new_series

        if isinstance(target_columns, list) and len(target_columns) == 1:
            target_columns = target_columns[0]
            logger.info(f"Single target column selected: {target_columns}")

        if isinstance(target_columns, str):
            # prepare target univariate series for Close price
            target_series = {
                t: stock_price_series[t].univariate_component(target_columns)
                for t in stock_price_series.keys()
            }
            logger.info(f"Preparing univariate target series: {target_columns}")
        else:
            # prepare target multivariate series for Open, Close and Volume
            target_series = {
                t: drop_non_target_columns(s) for t, s in stock_price_series.items()
            }
            logger.info(f"Preparing multivariate target series: {target_columns}")
        self.target_series = target_series

    def prepare_stock_price_series(self, train_date_start: pd.Timestamp = None):
        loaded_tickers = self.stock_price_dict.keys()
        logger.info(
            f"Preparing ticker series for {len(loaded_tickers)} stocks: \n{loaded_tickers}"
        )
        stock_price_series = {
            t: TimeSeries.from_dataframe(self.stock_price_dict[t], freq="B")
            for t in loaded_tickers
        }
        logger.info("Ticker series dict created.")
        filler = MissingValuesFiller()
        for t, series in stock_price_series.items():
            # gaps = series.gaps(mode="any")
            # logger.info(f'ticker: {t} gaps: \n {gaps}')
            series_filled = filler.transform(series)
            # check for any data gaps
            price_gaps = series_filled.gaps(mode="any")
            assert len(price_gaps) == 0
            # logger.info(f'ticker: {t} gaps after filler: \n {any_price_gaps}')
            stock_price_series[t] = series_filled
        logger.info("Filled missing values in ticker series.")
        for t, series in stock_price_series.items():
            stock_price_series[t] = series.slice(train_date_start, series.end_time())
            # logger.info(f'ticker: {t} , {ticker_series[t]}')
        # add holidays as future covariates
        logger.info("Aligned ticker series dict with train start date.")
        logger.info("Ticker series prepared.")
        return stock_price_series
