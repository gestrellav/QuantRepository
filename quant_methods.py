import pandas as pd
import numpy as np

class QuantMethods:
    @staticmethod
    def LogReturn(
        prices: pd.Series
    ) -> pd.Series:
        """
        Calcula el logaritmo del retorno de una serie de precios.
        """
        # Validación de entrada
        if not isinstance(prices, pd.Series):
            raise ValueError(""
            "La entrada debe ser una serie de pandas."
        )

        # Cálculo del logaritmo del retorno
        log_return = np.log(prices / prices.shift(1))

        return log_return.dropna()