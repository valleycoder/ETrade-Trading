from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message
from BusinessModels.OrderDetails import Instrument, OrderDetail
from BusinessModels.Settings import Settings


class Event:
    """ The Events associated with the Order. We are not using events information in the application.

        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/Event

        Attributes:

        Name - Name of the event.

        DateTime - The date and time of the order event. Epoch time.

        OrderNumber - Internal order number. This is different from OrderId.

        Instruments - Instruments associated with the order detail with OrderNumber.

    """
    def __init__(self):
        self.Name = ""
        self.DateTime = ""
        self.OrderNumber = 0
        self.Instruments:List[Instrument] = []


class Order:
    """ Represents the Order in the system.

        Attributes:

        OrderId - ID number assigned to this order.

        OrderType -  The type of Order. Only EQ is supported.

        TotalOrderValue - The total order value. Initialized with a predefined value to make sure that this
        field is actually populated by the API call.

        TotalCommission - The total commission. Initialized with a predefined value to make sure that this 
        field is actually populated by the API call.

        OrderDetails - The order details in this Order.

        Events - The events associated with the Order grouped by OrderNumber.

    """
    def __init__(self, orderId:int = 0, 
                    orderType: str = "",
                    orderDetails: List[OrderDetail] = [],
                    events: List[Event] = []
                    ):
        self.OrderId = orderId
        self.OrderType = orderType
        self.TotalOrderValue:float = Settings.UnfilledValue
        self.TotalCommission:float = Settings.UnfilledCommissionOrFee
        self.OrderDetails:List[OrderDetail] = orderDetails
        self.Events:List[Event] = events


class OrdersResponse:
    """ The Orders returned by the Orders API.

        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/OrdersResponse

        Attributes:

        Orders - The list of Orders.

        Messages - Any messages returned by the API call.

        Error - Response Error if any.

        Next - Url to the Next page of the Orders. Url also includes Marker.

        Marker - Denoting the position of the Next page of Orders.

    """

    def __init__(self, error: Error = None, orders: List[Order] = [], 
                    messages: List[Message] = []):
        self.Orders: List[Order] = orders
        self.Messages: List[Message] = messages
        self.Error: Error = error
        self.Next: str = ""
        self.Marker:str = ""        
