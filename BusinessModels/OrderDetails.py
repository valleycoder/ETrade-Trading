from typing import List

from BusinessModels.Message import Message
from BusinessModels.Settings import Settings


class Instrument:
    """ The data attributes involved with security trading is very broad. This class deals
        with the data specific to this application. This application deals with only EQ security type.

        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/Instrument

        Attributes:

        Symbol - The market symbol for the security being bought or sold.

        SecurityType - The type code to identify the order or leg request. Only EQ is supported. This can be Enum type.

        OrderAction - The action that the broker is requested to perform. Only BUY and SELL are supported. This can be Enum type.

        AverageExecutionPrice - The average execution price	for this specific order action.

        EstimatedCommission - Any commission applied. For small traders commission is very important attribute. I am initializing
        this field to a predefined value so that we can validate whether this field is being populated by the API or not. If this field is expected 
        to be filled by the API and not filled by the API - We abort the application. For small traders commission is very critical.

        EstimatedFees - Any fees applied. For small traders fee is very important attribute. I am initializing
        this field to a predefined value so that we can validate whether this field is being populated by the API or not. If this field is 
        expected to be filled by the API and not filled by the API - We abort the application. For small traders fee is very critical.

        FilledQuantity - The number of shares filled. In case of partial fill this field is populated.

        OrderedQuantity - The number of shares ordered.

        CancelQuantity - The number of shares to cancel ordering. This is not used in the application.

        QuantityType - The type of the quantity. Only QUANTITY is supported.

        Quantity - The number of shares to buy or sell.

    """
    def __init__(self):
        self.Symbol = ""
        self.SecurityType = ""
        self.OrderAction = ""
        self.AverageExecutionPrice = 0
        self.EstimatedCommission:float = Settings.UnfilledCommissionOrFee
        self.EstimatedFees:float = Settings.UnfilledCommissionOrFee
        self.FilledQuantity = 0
        self.OrderedQuantity = 0
        self.CancelQuantity = 0
        self.QuantityType = 0
        self.Quantity = 0


class OrderDetail:
    """ The order details are managed using this class objects. We are using only attributes required for this
        specific application.

        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/OrderDetail

        Attributes:

        OrderNumber - The numerical order number in a order. An order can have more than one order details.

        PlacedTime - The time the order was placed (UTC). Epoch time.

        ExecutedTime - The time the order was executed (UTC). Epoch time.

        OrderValue - Total cost or proceeds, including commission.

        MarketSession - The session in which the order will be placed. REGULAR, EXTENDED. This can be changed to Enum.

        StopPrice - The designated boundary price for a stop order. We are not using this field in the application.

        Status - The status of the order. OPEN, EXECUTED, CANCELLED, INDIVIDUAL_FILLS, PARTIAL and more. This can be changed to Enum.

        PriceType - The type of pricing. We only support LIMIT price. This can be Enum type.

        OrderTerm - The term for which the order is in effect. GOOD_UNTIL_CANCEL, GOOD_FOR_DAY. This can be Enum type.

        OrderType - The type of order being placed. Only EQ is supported. This can be Enum Type.

        AllOrNone - If TRUE, the transactions specified in the order must be executed all at once or not at all; default is FALSE.

        LimitPrice - The highest price at which to buy or the lowest price at which to sell if specified in a limit order.

        EstimatedCommission - Any commission applied. For small traders commission is very important attribute. I am initializing
        this field to a predefined value so that we can validate whether this field is being populated by the API or not. If this field is expected 
        to be filled by the API and not filled by the API - We abort the application. For small traders commission is very critical.

        EstimatedFees - Any fees applied. For small traders fee is very important attribute. I am initializing
        this field to a predefined value so that we can validate whether this field is being populated by the API or not. If this field is 
        expected to be filled by the API and not filled by the API - We abort the application. For small traders fee is very critical.

        EstimatedTotalAmount - The cost or proceeds, including broker commission, resulting from the requested action. I am initializing
        this field to a predefined value so that we can validate whether this field is being populated by the API or not. If this field is 
        expected to be filled by the API and not filled by the API - We abort the application.

        Instruments - Instruments related to this order detail. In our application case only one instrument will be present.

        Messages - Any message related to this order detail. This is populated by the API while 
        fetching/previewing/placing the order.

    """
    def __init__(self):
        self.OrderNumber:int = 0
        self.PlacedTime:int = 0
        self.ExecutedTime:int = 0
        self.OrderValue = 0
        self.MarketSession = ""
        self.StopPrice = 0
        self.Status = ""
        self.PriceType = ""
        self.OrderTerm = ""
        self.OrderType = ""
        self.AllOrNone = False
        self.LimitPrice:float = 0
        self.EstimatedCommission:float = Settings.UnfilledCommissionOrFee
        self.EstimatedFees:float = Settings.UnfilledCommissionOrFee
        self.EstimatedTotalAmount:float = Settings.UnfilledValue
        self.Instruments:List[Instrument] = []     
        self.Messages:List[Message] = []
