from enum import Enum, unique


@unique
class SellDeltaType(Enum):
    """ Represents the Sell interval type used to determine the Sell prices.

        FIXED - Sell price will be fixed.

        NEXTBUYPRICE - Sell price will be the next(forward) buy price.

        PERCENTAGE - Sell price will be percentage of the buy price.

    """
    FIXED = 1
    NEXTBUYPRICE = 2
    PERCENTAGE = 3
