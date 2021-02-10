from enum import Enum, unique


@unique
class MessageType(Enum):
    """ The type of message.

    """
    WARNING = 1
    INFO = 2
    ERROR = 3
    INFO_HOLD = 4
    FATAL = 5


class Message:
    """ API response messages are stored in this class objects.
        Mapping from API - https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/Message

        Attributes:

        Code - Numeric code.

        Description - Description of the error/info/warning.

        Type - WARNING/INFO/ERROR/INFO_HOLD/FATAL

    """
    def __init__(self, code:str = "", description:str = "", type:MessageType = MessageType.FATAL):
        self.Code:str = code
        self.Description:str = description
        self.Type:MessageType = type
