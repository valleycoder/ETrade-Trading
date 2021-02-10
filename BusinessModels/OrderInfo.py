class OrderInfo:
    """ Used to manage the EQ orders to be placed or cancelled. A minimal internal representation of
        the EQ order.

        Attributes:

        OrderId - Existing OrderId or some constant NewOrderId for non-existing order.

        Symbol - The Symbol of the Equity.

        LimitPrice - Interested Limit Price.

        Quantity - Quantity.

        IsPartialFilled - Is this Order partially filled?

        IsSell - Is this a Sell Order? Application deals only with BUY/SELL Orders.

    """
    def __init__(self, orderId:int, symbol:str, limitPrice:float, quantity:int, 
                    isPartialFilled:bool, isSell:bool = False):
        self.OrderId = orderId
        self.Symbol = symbol
        self.LimitPrice = limitPrice
        self.Quantity = quantity
        self.IsPartialFilled = isPartialFilled
        self.IsSell = isSell

    def __str__(self):
        """ String representation of the object.
        """
        return self.__repr__()

    def __repr__(self):
        """ String representation of the object.
        """
        partial:str = "FULL"
        if(self.IsPartialFilled is True):
            partial = "PARTIAL"

        action:str = "BUY"
        if(self.IsSell is True):
            action = "SELL"

        return f"[{self.Symbol}, {self.LimitPrice}, {self.Quantity}, {self.OrderId}, {action}, {partial}]"

    def __eq__(self, other): 
        if not isinstance(other, OrderInfo):
            # If unrelated types.
            return NotImplemented

        # Check attribute by attribute.
        return self.IsPartialFilled == other.IsPartialFilled and \
                self.Symbol == other.Symbol and \
                self.Quantity == other.Quantity and \
                self.OrderId == other.OrderId and \
                self.IsSell == other.IsSell and \
                self.LimitPrice == other.LimitPrice
