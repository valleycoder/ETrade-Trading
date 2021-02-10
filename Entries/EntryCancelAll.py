import os
import sys
import time
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))


from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.CancelOrderResponse import CancelOrderResponse
from BusinessModels.FilteringAndPagingParams import \
    OrdersFilteringAndPagingParams
from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError
from requests.exceptions import ConnectionError

from Entries.EntryHelpers.ErrorHandlingHelpers import (ProcessMessageError,
                                                       ProcessResponseError)
from Entries.EntryInputs.EntryOrderInput import EntryOrderInput


def CancelActiveStockOrders(entryInput:EntryOrderInput, activeStockItems:List[ActiveStockItem]):
    """ Cancel the orders of the given stock items.

        Parameters:

        entryInput:EntryOrderInput - Input object.

        activeStockItems:List[ActiveStockItem] - Stock items list.

    """
    proceed = True

    # Get the latest Access Keys and update the Input with the latest keys.
    # We can move the updation part to the EntryInput itself, but it's ok.
    accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
    entryInput.InputModel.AccessToken = accessToken
    entryInput.InputModel.AccessTokenSecret = accessTokenSecret
    entryInput.InputModel.AccessTokenDateTime = dateTimeObj

    # Update the Authorization and Order objects also.
    entryInput.Auth.inputModel = entryInput.InputModel
    entryInput.Order.inputModel = entryInput.InputModel

    try:
        
        # If there are stock items
        if activeStockItems is not None and len(activeStockItems) != 0:   
            activeStocks:List[ActiveStockItem] = [] 

            # Make a copy of the stock items and work with the copy.
            # We need copy because we are using a stack operations.
            for activeStockItem in activeStockItems:
                activeStocks.append(activeStockItem)

            # Do while there is an item in the Stack.
            while(len(activeStocks) != 0):    
                # Get the top stock item.
                currentStock:ActiveStockItem = activeStocks[0]
                orderFilteringAndPagingParams = OrdersFilteringAndPagingParams()
                orderFilteringAndPagingParams.PageSize = 100
                orderFilteringAndPagingParams.Params["symbol"] = currentStock.Symbol
                orderFilteringAndPagingParams.Params["status"] = "OPEN"
                # transactionType - BUY, SELL
                orderFilteringAndPagingParams.Params["securityType"] = "EQ"
                orderFilteringAndPagingParams.ApplyFilterAndReturnAll = True

                # Get all the orders.
                ordersResponse = entryInput.Order.Orders(accountIdKey= entryInput.ETradeSettings.AccountIdKey, 
                    accessToken= accessToken, 
                    accessTokenSecret= accessTokenSecret, 
                    filteringAndPagingParams= orderFilteringAndPagingParams)
            
                # Handle error. If error continue and try again.
                if(ordersResponse.Error is not None and ordersResponse.Error.ResponseStatusCode != ""):
                    ProcessResponseError(ordersResponse.Error, entryInput)
                    accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                    continue

                # Process messages and try again if required.
                if(ordersResponse.Messages is not None and len(ordersResponse.Messages) != 0):
                    if(ProcessMessageError(ordersResponse.Messages, entryInput) is False):
                        continue

                # Cancel the orders.           
                for cancelOrder in ordersResponse.Orders:
                    cancelOrderResponse:CancelOrderResponse = entryInput.Order.CancelOrder(accountIdKey= entryInput.ETradeSettings.AccountIdKey, 
                            orderId = cancelOrder.OrderId, accessToken = accessToken, accessTokenSecret=accessTokenSecret)

                    # Handle error. If error continue and try again.
                    if(cancelOrderResponse.Error is not None and cancelOrderResponse.Error.Code != ""):
                        ProcessResponseError(cancelOrderResponse.Error, entryInput)
                        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                        continue

                    # Process messages and try again if required.
                    if(cancelOrderResponse.Messages is not None and len(cancelOrderResponse.Messages) != 0):
                        if(ProcessMessageError(cancelOrderResponse.Messages, entryInput) is False):
                            continue

                    print(f"Cancelled Order {cancelOrder.OrderId}")                        

                # Get the orders to check if they are all cancelled or not.                               
                ordersResponse = entryInput.Order.Orders(accountIdKey= entryInput.ETradeSettings.AccountIdKey, 
                    accessToken= accessToken, 
                    accessTokenSecret= accessTokenSecret, 
                    filteringAndPagingParams= orderFilteringAndPagingParams)

                # Handle error if any.
                if(ordersResponse.Error is not None and ordersResponse.Error.Code != ""):
                    ProcessResponseError(ordersResponse.Error, entryInput)
                    accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                    continue

                # Process message if any.
                if(ordersResponse.Messages is not None and len(ordersResponse.Messages) != 0):
                    if(ProcessMessageError(ordersResponse.Messages, entryInput) is False):
                        continue
                
                # If count is zero. All orders are cancelled.
                # There is a problem with the API. It takes sometime to cancel
                # the orders completely. So we try again if all are not cancelled.
                if(ordersResponse.Orders is not None and len(ordersResponse.Orders) == 0):
                    print(f"All Orders of {currentStock.Symbol} are cancelled successfully.")    
                else:
                    print(f"Unable to cancel all the existing orders of {currentStock.Symbol}.")
                    time.sleep(1)
                    continue                                                

                # We come here, meaning all the Orders are cancelled.
                # Remove the item from the stack.
                activeStocks.pop(0)        

        else:
            print("No active items available.")            
        
        # We are here if everything is fine.
        return True

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
        entryInput.LogMessage(entryInput.Logger, f"Looks like internet connection issue - {connectionError}", True, True)
        proceed = False              
    except:
        entryInput.LogMessage(entryInput.Logger, entryInput.Strings.UnexpectedError.format(sys.exc_info()), True, True)
        proceed = False
        
    return proceed
    

if __name__ == "__main__":

    """ Cancels all the orders of the active stock items.
    """

    from Entries.ActiveStocks import ActiveStockItems

    entryInput = EntryOrderInput()
    count = 0

    # ReTry count.
    maxTryCount = 2

    while(True):
        # If Cancel all failed try again.
        if CancelActiveStockOrders(entryInput, ActiveStockItems) is False:
            print("Unable to cancel all existing orders.")
            count = count + 1
        else:
            print("Orders cancelled successfully.")      
            break
        
        # Break after trying maximum number of times.
        if(count == maxTryCount):
            break

        print(f"Trying again: {count + 1}")
        
