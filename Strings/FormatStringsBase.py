class FormatStringsBase:
    """ Inorder to avoid hardcoding strings in the Bussiness classes, the strings are
        stored in this classes attributes.        

        Please look at the class implementation for details.

        This will be helpful, if we need localized strings in future.

        With this in place, we can move the strings to the external storage easily.
        
    """
    InputStringsNone = "Argument strings is None"

    def __init__(self):
        self.InputNone = "Argument {0} is None"
        self.FatalErrorCode = "-999999"
        self.FatalUnhandledData = "FATAL - Unhandled data - {0}"
        self.FatalType = "FATAL"
        self.RequestHeader = "Request Header - {0}"
        self.ResponseBody = "Response Body - {0}"
        self.ResponseContent = "Response Content - {0}"
        self.ResponseCode = "Response Status Code - {0}"
        self.UnexpectedError = "Unexpected Error - {0}"
        self.UnexpectedValue = "Unexpected Value - {0} for {1}"
        self.FilteringAndPagingParamsError = "Invalid filteringAndPagingParams property {0} value - {1}"
        self.AuthorizeFailedForUnknownReason = "Authorize Failed for Unknown Reason."
        self.TokenExpired = "token_expired"
        self.TokenRejected = "token_rejected"
        self.InvalidTokenUsed = "Invalid access token used"
        self.SignatureInvalid = "signature_invalid"
