import pandas as pd
from typing import Union
import yfinance as yf
import logging
from constants import PriceType


class MarketData:    
    @staticmethod
    def get_market_data(
        tickers: list[str],
        start_date: str,
        end_date: str,
        price_type: PriceType = PriceType.Close # default
    ) -> Union[pd.Series, pd.DataFrame]:

        logger = logging.getLogger("MarketData.Prices")
        logger.info("Starting market data download process.")

        # ===== Validations ===== #
        # Tickers validation
        if not tickers or not isinstance(tickers, list):
            msg = "tickers must be a non-empty list."
            logger.error(msg)
            raise TypeError(msg)
        
        if not all(isinstance(t, str) for t in tickers):
            msg = "All tickers must be strings."
            logger.error(msg)
            raise TypeError(msg)
        
        # Dates validation
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            msg = "start_date and end_date must be strings in 'YYYY-MM-DD' format."
            logger.error(msg)
            raise TypeError(msg)

        logger.info(f"Tickers to download: {tickers}")
        logger.info(f"Date range: {start_date} to {end_date}")
        logger.info(f"Price type: {price_type.name}")
        
        # ===== Data Download ===== #
        try:
            raw = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                progress=False
            )

        except Exception as e:
            logger.exception("Error downloading data from yfinance.")
            raise RuntimeError(
                f"Error downloading data from yfinance. Exception: {e}"
                )
        
        # ===== Extract Column ===== #
        # Multiple tickers case
        if isinstance(raw.columns, pd.MultiIndex): # type: ignore
            if price_type.value not in raw.columns.get_level_values(0): # type: ignore
                raise ValueError(
                    f"'{price_type.value}' not found in downloaded data."
                )
            marketdata = raw[price_type.value] # type: ignore
        else:
            # Single ticker case
            if price_type.value not in raw.columns: # type: ignore
                raise ValueError(
                    f"'{price_type.value}' not found in downloaded data."
                )
            marketdata = raw[[price_type.value]].rename(columns={price_type.value: tickers[0]}) # type: ignore
        
        if marketdata.empty:
            raise ValueError(
                "Requested price data is empty."
            )
        
        logger.info(
            "Market data download and extraction completed successfully."
        )
        return marketdata