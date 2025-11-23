import pandas as pd
from market_data import MarketData
from quant_methods import QuantMethods

if __name__ == "__main__":
    # Definir los parámetros
    tickers = ["AAPL", "MSFT", "GOOGL"]
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # Obtener datos de mercado
    data = MarketData.Prices(tickers, start_date, end_date)
    print("Datos de mercado descargados:")
    print(market_data.head())

    # Calcular retornos logarítmicos
    log_returns = QuantMethods.LogReturn(tickers, market_data, lag=1)
    print("\nRetornos logarítmicos calculados:")
    print(log_returns.head())