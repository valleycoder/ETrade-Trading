import os
import sys
import time
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))


from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError
from requests.exceptions import ConnectionError

from Entries.EntryHelpers.ErrorHandlingHelpers import ProcessResponseError
from Entries.EntryInputs.EntryMarketInput import EntryMarketInput


def DoMarket(entryInput:EntryMarketInput, symbols:List[str]):
    """ Get the latest Quote of the list of the stocks.
        There are certian API limitations on the number of Symbols in the list.
        We are not considering those limitations.

        Parameters:

        entryInput:EntryMarketInput - entry input object.

        symbols:List[str] - List of symbols.

    """

    proceed = True
    while True:
        # Get the latest Access Keys and update the Input with the latest keys.
        # We can move the updation part to the EntryInput itself, but it's ok.
        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
        entryInput.InputModel.AccessToken = accessToken
        entryInput.InputModel.AccessTokenSecret = accessTokenSecret
        entryInput.InputModel.AccessTokenDateTime = dateTimeObj

        # Update the Authorization and Market objects.
        entryInput.Auth.inputModel = entryInput.InputModel
        entryInput.Market.inputModel = entryInput.InputModel
                        
        try:            
            # Get the Quotes. I think there is a limit of maximum 20 symbols in the list.
            quoteResponse = entryInput.Market.Quotes(symbols, accessToken, accessTokenSecret)

            # If error, process error and try again.
            if quoteResponse is not None and quoteResponse.Error is not None:
                ProcessResponseError(quoteResponse.Error, entryInput)
                # Get the latest tokens and try again.
                accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                continue
            
            # Display error messages if any.
            if quoteResponse is not None and quoteResponse.Messages is not None and len(quoteResponse.Messages) != 0:
                for i in range(len(quoteResponse.Messages)):
                    print("Message Code is ", i, " -> ", quoteResponse.Messages[i].Code)
                    print("Message Type is ", i, " -> ", quoteResponse.Messages[i].Type.name)
                    print("Message Description is ", i, " -> ", quoteResponse.Messages[i].Description)

            # Display the Quote information.
            if quoteResponse is not None and quoteResponse.QuoteData is not None and len(quoteResponse.QuoteData) != 0:
                for i in range(len(quoteResponse.QuoteData)):
                    print("dateTime ->", i, " -> ", quoteResponse.QuoteData[i].DateTime)
                    print("Symbol ->", i, " -> ", quoteResponse.QuoteData[i].Symbol)
                    print("Last Price ->", i, " -> ", quoteResponse.QuoteData[i].LastTradedPrice)
                    print("Adjusted Flag ->", i, " -> ", quoteResponse.QuoteData[i].AdjustedFlag)

            return
        
        except MessageError as message:        
            entryInput.LogMessage(entryInput.Logger, entryInput.Strings.UnexpectedError.format(message.Message.Type.name), True, True)
            entryInput.LogMessage(entryInput.Logger, entryInput.Strings.UnexpectedError.format(message.Message.Code), True, True)
            entryInput.LogMessage(entryInput.Logger, entryInput.Strings.UnexpectedError.format(message.Message.Description), True, True)
            proceed = False
        except ResponseError as error:
            entryInput.LogMessage(entryInput.Logger, f"Error status code - {error.Error.ResponseStatusCode}", True, True)
            entryInput.LogMessage(entryInput.Logger, f"Error code - {error.Error.Code}", True, True)
            entryInput.LogMessage(entryInput.Logger, f"Error message - {error.Error.Message}", True, True)
            proceed = False            
        except ConnectionError as connectionError:
            # Internet connection error. We can try again.
            entryInput.LogMessage(entryInput.Logger, f"Looks like internet connection issue - {connectionError}", True, True)
            proceed = True        
        except:
            entryInput.LogMessage(entryInput.Logger, entryInput.Strings.UnexpectedError.format(sys.exc_info()), True, True)
            proceed = False
            
        # If proceed is False, something blocking happened, so we cannot continue.
        if(proceed is False):
            break

        # Wait for 5 seconds and try again.
        time.sleep(5)
        

if __name__ == "__main__":

    """ Get the quote information of the list of the stocks.
    """
    entryInput = EntryMarketInput()
    DoMarket(entryInput, ['GE', 'MSFT', 'XXXX'])
