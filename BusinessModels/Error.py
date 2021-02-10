class Error:
    """ Class to store API response errors

        Attributes:

        ResponseStatusCode - API response code.

        Code - Error code.

        Message - Error description if the message is in JSON.
        Entire error message with Code if the message is not in JSON format.

    """
    def __init__(self, responseStatusCode:str, code:str, message:object):
        self.ResponseStatusCode = responseStatusCode
        self.Code:str = code
        self.Message:object = message
