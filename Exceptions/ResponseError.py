from BusinessModels.Error import Error

from Exceptions.ErrorException import Error as ExceptionError


class ResponseError(ExceptionError):
    """ Exception used to represent any critical Error.

        Attributes:

        Error:Error - Error object associated with this Exception.

    """
    def __init__(self, error:Error):
        self.Error:Error = error
