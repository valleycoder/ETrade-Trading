from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message
from BusinessModels.OrderDetails import OrderDetail
from BusinessModels.Settings import Settings


class PreviewId:
    """ Class maintaining PreviewId of the preview order.

        Attributes:

        PreviewId - PreviewId of the preview order.

        CashMargin - The cash margin designation. CASH, MARGIN - We don't support margin trading.

    """
    def __init__(self):
        self.PreviewId:int = 0
        self.CashMargin:str = ""


class PreviewOrderResponseData:
    """ The response data received from a successful preview order request. For recording purposes, the preview order related 
        input to the request is also stored in the response object.

        Attributes:

        PreviewOrderInput - The input to the place order should be exactly same as the input sent to the
        preview order. For recording purposes the input sent to the preview order is also included in the
        preview order response.

        PreviewIds - PreviewId which is required to place the final order.

        TotalCommission - Total commission. We expect the API to fill this field and inorder to verify this we initialize it with a reasonably 
        unique constant value.

        TotalOrderValue - Total order value. We expect the API to fill this field and inorder to verify this we initialize it with a reasonably 
        unique constant value.

        ClientOrderId - ClientOrderId is required to preview the Order. This should be unique.

        OrderDetails - The order details of the preview Order.

    """
    def __init__(self):
        self.PreviewOrderInput = None
        self.PreviewIds: List[PreviewId] = []
        self.TotalCommission = Settings.UnfilledCommissionOrFee
        self.TotalOrderValue = Settings.UnfilledValue
        self.ClientOrderId = ""
        self.OrderDetails:List[OrderDetail] = []


class PreviewOrderResponse:
    """ Preview order response.

        Attributes:

        PreviewOrderResponseData - Data on successful preview response.

        Messages - Message if any.

        Error - Error if any.
    """
    def __init__(self, error: Error = None, previewOrderResponseData: PreviewOrderResponseData = None, 
                        messages: List[Message] = []):
        self.PreviewOrderResponseData:PreviewOrderResponseData = previewOrderResponseData
        self.Messages: List[Message] = messages
        self.Error: Error = error
