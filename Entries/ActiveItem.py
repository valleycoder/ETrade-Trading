from BusinessModels.SellDeltaType import SellDeltaType


class ActiveItem:
    """ A class used to represent the stock item in the UI. Basically UI model for the stock item.

        Attributes:

        Symbol:str - Stock symbol.

        StartPrice:float - Start price.

        BuyStepSize:float - Buy intervals. Applied when quantity is greater than 0.

        SellStepSize:float - Sell profit. Applied when the SellStepType is FIXED or PERCENTAGE.

        SellStepType:SellDeltaType - Option to decide on the Sell price.
        When FIXED - SellStepSize value is used as profit amount per stock.
        When PERCENTAGE - SellStepSize value is used as percentage.
        When NEXTBUYPRICE - Sell price is the next(forward) BUY price.

        Quantity:int - The fixed quantity for the stock. It's convention based.
        When the quantity is greater than 0 - The Qualitity in the field is used.
        When the quantity is 0 - PriceCoordinates0 is applied.
        When the quantity is -1 - PriceCoordinates1 is applied and so on.

        MaxActiveBuy:int - Maximum number of active BUY orders for this stock.

        QuantityMultiplier:int - Used to multiply the quantity. Should be useful in case of 
        Split(Reverse Split) or used to avoid creating another PriceCoordinate

    """
    def __init__(self, symbol:str, startPrice: float, 
                buyStepSize:float = 0, sellStepSize: float = 0, 
                sellStepType:SellDeltaType = SellDeltaType.FIXED, quantity:int = 0,
                maxActiveBuy:int = 0, quantityMultiplier:int = 1):
        self.Symbol:str = symbol
        self.StartPrice:float = startPrice
        self.BuyStepSize:float = buyStepSize
        self.SellStepSize:float = sellStepSize
        self.SellStepType:SellDeltaType = sellStepType
        self.Quantity:int = quantity
        self.MaxActiveBuy:int = maxActiveBuy
        self.QuantityMultiplier:int = quantityMultiplier
        