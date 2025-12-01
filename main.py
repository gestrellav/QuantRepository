import pandas as pd
from market_data import MarketData
from quant_methods import QuantMethods
from prefect import flow, task

@flow
def main():
    # Definir los parámetros
    tickers = ["AAPL", "MSFT", "AMZN"]
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # Obtener datos de mercado
    data = MarketData.Prices(tickers, start_date, end_date) # type: ignore
    print("Datos de mercado descargados:")
    print(data.head())
    
    # Calcular retornos logarítmicos
    log_returns = QuantMethods.LogReturn(tickers, data, lag=1)
    print("\nRetornos logarítmicos calculados:")
    print(log_returns.head())