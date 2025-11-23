import pandas as pd
from typing import Union
import yfinance as yf
from prefect import get_run_logger


class MarketData:
    @staticmethod
    def Prices(
        tickers: list[str],
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        
        # Obtener el logger de Prefect
        logger = get_run_logger()
        logger.info("Iniciando descarga de datos de mercado.")
        
        # Validaciones básicas
        if not isinstance(tickers, list) or not all(isinstance(t, str) for t in tickers):
            logger.error("tickers debe ser una lista de strings.")
            raise TypeError("tickers debe ser una lista de strings.")
        
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            logger.error("start_date y end_date deben ser strings.")
            raise TypeError("start_date y end_date deben ser strings.")
        
        logger.info(f"Iniciando descarga de datos para {tickers}")
        logger.info(f"Rango de fechas: {start_date} a {end_date}")

        # Descarga de datos
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

        close_prices = data["Close"]

        # Validar que no está vacío
        if close_prices.empty:
            raise ValueError("No se obtuvieron datos de mercado para los tickers especificados.")

        # Convertir Series a DataFrame si solo viene 1 ticker
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame(name=tickers[0])

        return close_prices


