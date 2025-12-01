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
            raise RuntimeError(f"Error downloading data from yfinance. Exception: {e}")
        
        # ===== Extract Column ===== #
        # Multiple tickers case
        if isinstance(raw.columns, pd.MultiIndex):
            if price_type.value not in raw.columns.get_level_values(0):
                raise ValueError(f"'{price_type.value}' not found in downloaded data.")
            marketdata = raw[price_type.value]
        else:
            # Single ticker case
            if price_type.value not in raw.columns:
                raise ValueError(f"'{price_type.value}' not found in downloaded data.")
        
        



        # Validar que no está vacío
        if close_prices.empty:
            raise ValueError("No se obtuvieron datos de mercado para los tickers especificados.")

        # Convertir Series a DataFrame si solo viene 1 ticker
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame(name=tickers[0])

        return close_prices