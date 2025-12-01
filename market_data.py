import pandas as pd
from typing import Union
import yfinance as yf
import logging
from enum import Enum

class PriceType(Enum):
    ClosePrices = "Close"
    Adjusted = "Adj Close"
    Volume = "Volume"

class StockMarketData:
    @staticmethod
    def MarketData(
        tickers: list[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:

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

        logger.info(f"Tickers requested: {tickers}")
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # ===== Data Download ===== #
        try:
            data = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                progress=False
            )
            logger.info("Datos descargados exitosamente.")
        except Exception as e:
            logger.error(f"Error al descargar datos: {e}")
            raise RuntimeError(f"Error al descargar datos: {e}")
        
        # Validar que 'Close' existe (yfinance a veces cambia estructura)
        if "Close" not in data.columns:
            raise ValueError("El DataFrame descargado no contiene la columna 'Close'.")

        close_prices = data[Type.value]

        # Validar que no está vacío
        if close_prices.empty:
            raise ValueError("No se obtuvieron datos de mercado para los tickers especificados.")

        # Convertir Series a DataFrame si solo viene 1 ticker
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame(name=tickers[0])

        return close_prices