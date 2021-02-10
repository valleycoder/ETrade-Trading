from BusinessModels.PriceCoordinate import PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType

from typing import List


class ActiveStockItem:
    """ Represents an active stock item. An active item is a stock which we are currently trading in the
        system. Very critical class in the application. Please be very careful before changing the 
        attribute values of the objects of this class.

        Attributes:

        Symbol - Stock symbol.

        StartPrice - The start price from which we start applying the algorithm. Please be very careful before
        changing the start price when the stock is already purchased and present in the portfolio.
        If the stock is already in the portfolio and if you reduce the start price, you will end up selling
        the purchased stocks for a loss.

        PriceCoordinates - Pricecoorinates used to calculate the buy prices and quantities.

        SellStepType - The sell type used for this item. 
        when FIXED -> sellprice = (buyprice + SellStepSize).
        when NEXTBUYPRICE -> sell price is next buy price.
        when PERCENTAGE -> sell price is percentage of SellStepSize

        SellStepSize - The profit for which the stock is sold. The value can be either profit value or 
        profit percentage. Commission and fees are not included.
        Please make sure that the SellStepSize is positive. I am not doing input validations.

        MaxActiveBuy -  The maximum number of active BUY orders for the stock at any given time.

        QuantityMultiplier - Multiplies the quantity returned by the priceCoordinates with the QuantityMultiplier. This field
        is used to increase the quantity by QuantityMultiplier times.

    """
    def __init__(self, symbol:str, startPrice: float = 0, 
                priceCoordinates:List[PriceCoordinate] = None, 
                sellStepType: SellDeltaType = SellDeltaType.NEXTBUYPRICE,
                sellStepSize: float = 0, 
                maxActiveBuy:int = 0, quantityMultiplier:int = 1):
        self.Symbol:str = symbol
        self.StartPrice: float = startPrice
        self.PriceCoordinates:List[PriceCoordinate] = priceCoordinates
        self.SellStepType:SellDeltaType = sellStepType
        self.SellStepSize: float = sellStepSize
        self.MaxActiveBuy:int = maxActiveBuy
        self.QuantityMultiplier:int = quantityMultiplier