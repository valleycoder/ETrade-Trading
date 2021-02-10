from datetime import datetime
from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message, MessageType
from Entries.EntryInputs.EntryInput import EntryInput
from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError


def ProcessResponseError(error:Error, entryInput:EntryInput):
    """ Handles the response error returned by the API.

        If error is 401 - Try to Renew the token or authorize and get new token and also 
        stores the latest tokens.
        If error code is one present in the Exclusions then this is a safe error.
        If the error code is not something unexpected then raise ResponseError exception.

        Parameters:

        error:Error - The error object populated by the API.

        entryInput:EntryInput - The base entryInput object. It contains most of the
        objects the Entry script has access to.

        Exceptions:

        ResponseError, Exception.        

    """

    # Log the Error information.
    entryInput.LogMessage(entryInput.Logger, f"Error status code - {error.ResponseStatusCode}", True, True)
    entryInput.LogMessage(entryInput.Logger, f"Error code - {error.Code}", True, True)
    entryInput.LogMessage(entryInput.Logger, f"Error message - {error.Message}", True, True)

    # If error is 401 - Try to Renew the token or authorize and get new token. Store the latest token.
    # If error code is one present in the Exclusions then this is a safe error.
    # If the error code is not something unexpected then raise ResponseError exception.
    if(error.ResponseStatusCode == 401):
        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
        if entryInput.Strings.TokenExpired in str(error.Message) or entryInput.Strings.SignatureInvalid in str(error.Message) or entryInput.Strings.InvalidTokenUsed in str(error.Message):
            accessToken, accessTokenSecret = entryInput.Auth.Authorize(entryInput.Settings.IsAuthorizationManual, entryInput.Settings.ChromeDriverPathWithName)
            if accessToken == "" or accessTokenSecret == "":
                raise Exception(entryInput.Strings.AuthorizeFailedForUnknownReason)
            entryInput.Configuration.StoreETradeAccessKeys(accessToken, accessTokenSecret, datetime.now())
        elif entryInput.Strings.TokenRejected in str(error.Message):
            status = entryInput.Auth.RenewAccessToken(accessToken, accessTokenSecret)
            if status == 200:
                entryInput.Configuration.StoreETradeAccessKeys(accessToken, accessTokenSecret, datetime.now())
            elif status == 401:
                accessToken, accessTokenSecret = entryInput.Auth.Authorize(entryInput.Settings.IsAuthorizationManual, entryInput.Settings.ChromeDriverPathWithName)
                if accessToken == "" or accessTokenSecret == "":
                    raise Exception(entryInput.Strings.AuthorizeFailedForUnknownReason)
                entryInput.Configuration.StoreETradeAccessKeys(accessToken, accessTokenSecret, datetime.now())
            else:
                raise Exception(entryInput.Strings.UnexpectedValue.format(status, "Status Code"))        
        else:
            raise Exception(entryInput.Strings.UnexpectedValue.format(error.Message, "Error Message"))
    elif(error.Code in entryInput.ETradeSettings.ExclusionErrorCodes):
        return True
    else:        
        raise ResponseError(error)     

    return True              


def ProcessMessageError(messages:List[Message], entryInput:EntryInput):
    """ Processes the API Messages.
        We are only concerned about the messages with MessageType ERROR, FATAL and Message codes
        in the DangerErrorCodes.

        Parameters:
        
        messages:List[Message] - List of the messages returned by the API.

        entryInput:EntryInput - The base entryInput object. It contains most of the
        objects the Entry script has access to.

        Exceptions:

        MessageError        

    """

    # If Message Type is ERROR or FATAL raise MessageError.
    for message in messages:
        if((message.Type == MessageType.ERROR) or (message.Type == MessageType.FATAL)):
            raise MessageError(message, messages)
    
    # If the Message Code is in DangerErrorCodes raise MessageError.
    for message in messages:        
        if(message.Code in entryInput.ETradeSettings.DangerErrorCodes):
            entryInput.LogMessage(entryInput.Logger, f"Message type - {message.Type.name}", True, True)
            entryInput.LogMessage(entryInput.Logger, f"Message Code - {message.Code}", True, True)
            entryInput.LogMessage(entryInput.Logger, f"Message Description - {message.Description}", True, True)
            raise MessageError(message, messages)

    return True
