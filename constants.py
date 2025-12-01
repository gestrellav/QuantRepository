from enum import Enum

class PriceType(Enum):
    Close = "Close"
    Adjusted = "Adj Close"
    Volume = "Volume"