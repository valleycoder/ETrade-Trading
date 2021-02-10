import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.AccountListResponse import AccountListResponse
from BusinessModels.FilteringAndPagingParams import \
    PortfolioFilteringAndPagingParams
from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError
from requests.exceptions import ConnectionError

from Entries.EntryHelpers.ErrorHandlingHelpers import ProcessResponseError
from Entries.EntryInputs.EntryAccountInput import EntryAccountInput


def DoAccount(entryInput:EntryAccountInput):
    """ Gets the list of accounts associated with the ConsumerKey and ConsumerSecret.
        Picks the first account returned and tries to get the portfolio items in the
        first account.

        If the AccessToken and AccessTokenSecret are invalid then the program tries
        to acquire new tokens and tries again in the while loop.
        
    Parameters:

    entryInput:EntryAccountInput - Input required to get the account information.

    """                                
    proceed = True                                
    while True:

        # Get the latest Access Keys and update the Input with the latest keys.
        # We can move the updation part to the EntryInput itself, but it's ok.
        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
        entryInput.InputModel.AccessToken = accessToken
        entryInput.InputModel.AccessTokenSecret = accessTokenSecret
        entryInput.InputModel.AccessTokenDateTime = dateTimeObj

        # Update the input model of the Authorization object.
        entryInput.Auth.inputModel = entryInput.InputModel

        try:

            # Get the account list.
            accountListResponse:AccountListResponse
            accountListResponse = entryInput.Account.AccountList(accessToken, accessTokenSecret)

            # Process Response Error If any.
            if accountListResponse is not None and accountListResponse.Error is not None:
                ProcessResponseError(accountListResponse.Error, entryInput)
                # Get the latest access keys from the config file and try again.             
                accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                continue

            # Print the list of the accounts.
            if accountListResponse is not None and accountListResponse.AccountData is not None and len(accountListResponse.AccountData) != 0:
                print("************Account List Begin***********************")
                for i in range(len(accountListResponse.AccountData)):
                    print("AccountId ->", i, " -> ", accountListResponse.AccountData[i].AccountId)
                    print("AccountIdKey ->", i, " -> ", accountListResponse.AccountData[i].AccountIdKey)
                    print("AccountDesc ->", i, " -> ", accountListResponse.AccountData[i].AccountDesc)
                print("****************Account List End*********************")

            # Get the portfolio items of the first account.
            if len(accountListResponse.AccountData) != 0:
                portfolioFilteringAndPagingParams = PortfolioFilteringAndPagingParams(pageSize=4, pageNumber=1)
                portfolioFilteringAndPagingParams.ApplyFilterAndReturnAll = True
                portfolioFilteringAndPagingParams.Params["xxxxx"] = "OO"
                portfolioResponse = entryInput.Account.Portfolio(accountListResponse.AccountData[0].AccountIdKey, 
                                                    accessToken = accessToken, 
                                                    accessTokenSecret = accessTokenSecret,
                                                    filteringAndPagingParams= portfolioFilteringAndPagingParams
                                                    )
                print("************Portfolio items***********************")
                if portfolioResponse is not None and portfolioResponse.Error is not None:
                    # Process response error if any.
                    ProcessResponseError(accountListResponse.Error, entryInput)
                    # Get the latest access keys from the config file and try again.               
                    accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                    continue
                else:  
                    # Print the portfolio items.
                    if portfolioResponse is not None and portfolioResponse.AccountPortfolios is not None and \
                        len(portfolioResponse.AccountPortfolios) != 0:
                        j:int = 1
                        for accountPortfolio in portfolioResponse.AccountPortfolios:
                            for portfolioPosition in accountPortfolio.PortfolioPositions:
                                print(j, " -> ", "Symbol - ", portfolioPosition.Symbol, "Quantity - ",portfolioPosition.Quantity)
                                j = j + 1
                print("************Portfolio itemsEnd ***********************")

            # We came here meaning we got everything we needed.
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
            # If internet connection issue we can try again.
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
    """ Program used to display the list of accounts for a 
        given consumerKey and consumerSecret.

        It also displays the portfolio items of the first account.
    """
    entryInput = EntryAccountInput()
    DoAccount(entryInput)
