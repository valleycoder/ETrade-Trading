from typing import List

from BusinessModels.Error import Error
from BusinessModels.Message import Message


class QuoteData:
    """ Subset of data retrieved from the Quote API.

        Attributes:

        DateTime - The date and time of the quote.

        Symbol - Symbol of the Quote.

        SecurityType - Type of the Security.

        LastTradedPrice - Last traded price.

        AdjustedFlag - Indicates whether an option has been adjusted due to a corporate 
        action (for example, a dividend or stock split)	
        
    """
    def __init__(self, dateTime:str = "", symbol:str = "", securityType:str = "", 
                    lastTradedPrice:str = "", adjustedFlag:bool = False):
        self.DateTime = dateTime
        self.Symbol = symbol
        self.SecurityType = securityType
        self.LastTradedPrice = lastTradedPrice
        self.AdjustedFlag = adjustedFlag


class QuoteResponse:
    """ Quote response.

        Attributes:

        QuoteData - Data on successful response.

        Messages - Message if any.

        Error - Error if any.

    """
    def __init__(self, error: Error = None, quoteData: List[QuoteData] = [], messages: List[Message] = []):
        self.QuoteData: List[QuoteData] = quoteData
        self.Messages: List[Message] = messages
        self.Error: Error = error
