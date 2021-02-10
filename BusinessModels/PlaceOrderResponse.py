from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message
from BusinessModels.OrderDetails import OrderDetail
from BusinessModels.PreviewOrderInput import PreviewOrderInput
from BusinessModels.Settings import Settings


class OrderId:
    """ Class maintaining OrderId of the placed order.

        Attributes:

        OrderId - OrderId of the placed order.

        CashMargin - The cash margin designation. CASH, MARGIN - We don't support margin trading.

    """
    def __init__(self):
        self.OrderId:int = 0
        self.CashMargin:str = ""


class PlaceOrderResponseData:
    
    """ The response data received from a successful place order request. For recording purposes, the order related 
        input to the request is also stored in the response object.

        Attributes:

        PreviewOrderInput - The input to the place order should be exactly same as the input sent to the
        preview order. For recording purposes the input sent to the place order is also included in the
        place order response.

        OrderId - OrderId of the placed order. If this is zero then OrderId should be present in OrderIds

        OrderIds - For a successful response if OrderId is zero then orderId should be in the OrderIds.

        TotalCommission - Total commission. We expect the API to fill this field and inorder to verify this we initialize it with a reasonably 
        unique constant value.

        TotalOrderValue - Total order value. We expect the API to fill this field and inorder to verify this we initialize it with a reasonably 
        unique constant value.

        ClientOrderId - ClientOrderId is required to place the Order. This should be unique like GUID

        OrderDetails - The order details of the placed Order.

    """
    def __init__(self):
        self.PreviewOrderInput:PreviewOrderInput = None
        self.OrderId:int = 0
        self.OrderIds: List[OrderId] = []
        self.TotalCommission:float = Settings.UnfilledCommissionOrFee
        self.TotalOrderValue:float = Settings.UnfilledValue
        self.ClientOrderId:str = ""
        self.OrderDetails:List[OrderDetail] = []


class PlaceOrderResponse:

    """ Place order response.

        Attributes:

        PlaceOrderResponseData - Data on successful response.

        Messages - Message if any.

        Error - Error if any.
    """

    def __init__(self, error: Error = None, placeOrderResponseData: PlaceOrderResponseData = None, 
                        messages: List[Message] = []):
        self.PlaceOrderResponseData:PlaceOrderResponseData = placeOrderResponseData
        self.Messages: List[Message] = messages
        self.Error: Error = error
