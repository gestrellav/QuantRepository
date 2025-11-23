import pandas as pd
import numpy as np
from typing import Union

class QuantMethods:
    @staticmethod
    def LogReturn(
        tickers: list[str],
        prices: Union[pd.DataFrame, pd.Series],
        lag: int = 1
    ) -> Union[pd.DataFrame, pd.Series]:

        if not isinstance(tickers, list) or not all(isinstance(t, str) for t in tickers):
            raise TypeError("tickers debe ser una lista de strings.")

        if not isinstance(prices, (pd.Series, pd.DataFrame)):
            raise TypeError("prices debe ser Series o DataFrame.")

        if not isinstance(lag, int) or lag < 1:
            raise ValueError("lag debe ser un entero positivo.")
        
        # Caso: prices es Series → validación estricta
        if isinstance(prices, pd.Series):
            if len(tickers) != 1:
                raise ValueError("Si prices es Series, solo se puede pasar un ticker.")
            price_series = prices
            log_ret = np.log(price_series / price_series.shift(lag))
            return log_ret.rename(tickers[0]) # type: ignore

        # Caso: prices es DataFrame
        results = []
        for ticker in tickers:
            if ticker not in prices.columns:
                raise ValueError(f"El ticker '{ticker}' no está en el DataFrame.")
            
            series = prices[ticker].where(prices[ticker].notna(), np.nan)
            log_ret = np.log(series / series.shift(lag))
            results.append(log_ret.rename(ticker)) #type: ignore
        
        return pd.concat(results, axis=1)

        