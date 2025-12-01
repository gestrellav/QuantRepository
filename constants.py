from enum import Enum

class PriceType(Enum):
    ClosePrices = "Close"
    Adjusted = "Adj Close"
    Volume = "Volume"