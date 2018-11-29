from enum import Enum

class Rating(Enum):

    SELL = -1
    HOLD = 0
    BUY = 1
    NONE = 404