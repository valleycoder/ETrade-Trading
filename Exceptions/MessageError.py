from typing import List

from BusinessModels.Message import Message

from Exceptions.ErrorException import Error as ExceptionError


class MessageError(ExceptionError):
    """ Exception used to represent any critical Message error.

        Attributes:

        Message:Message - First Message which requires attention.

        Messages:List[Message] - Complete list of messages.

    """
    def __init__(self, message:Message, messages:List[Message] = []):
        self.Message:Message = message
        self.Messages:List[Message] = messages
