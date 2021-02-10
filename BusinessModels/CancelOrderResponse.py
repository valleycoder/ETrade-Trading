from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message


class CancelOrderResponse:
    """ Represents the response returned by the Cancel Order API call.

        Attributes:

        OrderId - OrderId of the cancelled order.

        Messages - Any warning/error/info messages returned by the API.

        Error - Any response error returned by the API.

    """

    def __init__(self, orderId:int = 0, error: Error = None, 
                        messages: List[Message] = []):
        self.OrderId:int = orderId
        self.Messages: List[Message] = messages
        self.Error: Error = error
