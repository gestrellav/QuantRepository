from enum import Enum

class PriceType(Enum):
    Close = "Close"
    Volume = "Volume"
    High = "High"
    Low = "Low"
    Open = "Open"
    OHLC = ["Open", "High", "Low", "Close"]