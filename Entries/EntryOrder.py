import os
import sys
import time
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))


from BusinessModels.CancelOrderResponse import CancelOrderResponse
from BusinessModels.FilteringAndPagingParams import \
    OrdersFilteringAndPagingParams
from BusinessModels.OrderDetails import Instrument, OrderDetail
from BusinessModels.OrdersResponse import OrdersResponse
from BusinessModels.PreviewOrderInput import PreviewOrderInput
from BusinessModels.PreviewOrderResponse import PreviewOrderResponse
from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError
from requests.exceptions import ConnectionError

from Entries.EntryHelpers.ErrorHandlingHelpers import (ProcessMessageError,
                                                       ProcessResponseError)
from Entries.EntryInputs.EntryOrderInput import EntryOrderInput


def DoOrder(entryInput:EntryOrderInput):
    """ This function shows how to get a filtered list of orders, preview order,
        place order and cancel order.

        Orders filtering information is hardcoded.
        Order input is hardcoded.

    Parameters:

    entryInput:EntryOrderInput - Entry input object.

    """

    proceed = True
    while True:

        # Get the latest Access Keys and update the Input with the latest keys.
        # We can move the updation part to the EntryInput itself, but it's ok.        
        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
        entryInput.InputModel.AccessToken = accessToken
        entryInput.InputModel.AccessTokenSecret = accessTokenSecret
        entryInput.InputModel.AccessTokenDateTime = dateTimeObj

        # Update Authorization and Order objects.
        entryInput.Auth.inputModel = entryInput.InputModel
        entryInput.Order.inputModel = entryInput.InputModel
        
        try:

            # Example showing some orders filters.
            ordersResponse:OrdersResponse
            orderFilteringAndPagingParams = OrdersFilteringAndPagingParams()
            orderFilteringAndPagingParams.PageSize = 100
            # orderFilteringAndPagingParams.Params["fromDate"] = "09012020"
            # orderFilteringAndPagingParams.Params["toDate"] = "09012020"
            orderFilteringAndPagingParams.Params["symbol"] = "DAL"
            orderFilteringAndPagingParams.Params["status"] = "EXECUTED"
            # orderFilteringAndPagingParams.Params["xxxx"] = "OO"
            orderFilteringAndPagingParams.ApplyFilterAndReturnAll = True

            # Apply filters and get orders.
            ordersResponse = entryInput.Order.Orders(accountIdKey= entryInput.ETradeSettings.AccountIdKey, 
                accessToken= accessToken, 
                accessTokenSecret= accessTokenSecret, 
                filteringAndPagingParams= orderFilteringAndPagingParams)
            
            # Display the number of orders.
            print(len(ordersResponse.Orders))

            # Create a preview order input with hardcoded values.
            # We are trying to preview and place order for FB at 200.
            previewOrderResponse:PreviewOrderResponse
            previewOrderInput = PreviewOrderInput()
            previewOrderInput.ClientOrderId = "123ABC" + str(int(time.time())) 
            previewOrderInput.OrderType = "EQ"
            previewOrderInput.Order = []

            orderDetail = OrderDetail()
            orderDetail.AllOrNone = "true"
            orderDetail.PriceType = "LIMIT"
            orderDetail.OrderTerm = "GOOD_UNTIL_CANCEL"
            orderDetail.MarketSession = "REGULAR"
            orderDetail.StopPrice = ""
            orderDetail.LimitPrice = "200"
            orderDetail.Instruments = []

            instrument = Instrument()
            instrument.SecurityType = "EQ"
            instrument.Symbol = "FB"
            instrument.OrderAction = "BUY"
            instrument.QuantityType = "QUANTITY"
            instrument.Quantity = "1"

            orderDetail.Instruments.append(instrument)
            previewOrderInput.Order.append(orderDetail)

            # Preview the Order.
            previewOrderResponse = entryInput.Order.PreviewOrderEQ(accountIdKey= entryInput.ETradeSettings.AccountIdKey, previewOrderInput = previewOrderInput,
                accessToken= accessToken, 
                accessTokenSecret= accessTokenSecret, 
            )
                
            print(previewOrderResponse)
    
            # On error, process error and try again.
            if previewOrderResponse is not None and previewOrderResponse.Error is not None:
                ProcessResponseError(previewOrderResponse.Error, entryInput)
                accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                continue

            # On message, process message and try again if required.
            if(previewOrderResponse.Messages is not None and len(previewOrderResponse.Messages) != 0):
                if(ProcessMessageError(previewOrderResponse.Messages, entryInput) is False):
                    continue
 
            # Print preview response details.
            if previewOrderResponse is not None and previewOrderResponse.PreviewOrderResponseData is not None:
                print("************Preview Order Response Begin***********************")
                print("Total Commission -> ", previewOrderResponse.PreviewOrderResponseData.TotalCommission)
                for previewId in previewOrderResponse.PreviewOrderResponseData.PreviewIds:
                    print("previewId - >", previewId.PreviewId)

                orderDetails:List[OrderDetail] = previewOrderResponse.PreviewOrderResponseData.OrderDetails
                for orderDetail in orderDetails:
                    print("Estimated commission -> ", orderDetail.EstimatedCommission)
                    print("Estimated Fees -> ", orderDetail.EstimatedFees)
                    instruments:List[Instrument] = orderDetail.Instruments
                    for instrument in instruments:
                        print("Symbol - Quantity -> ", instrument.Symbol, instrument.Quantity)
                        print("EstimatedCommission -> ", instrument.EstimatedCommission)
                        print("EstimatedFees -> ", instrument.EstimatedFees)
                print("************Preview Order Response End***********************")

                """  
                # Place order.
                placedOrderId:int = 0            
                if previewOrderResponse is not None and \
                    previewOrderResponse.PreviewOrderResponseData is not None and \
                    previewOrderResponse.PreviewOrderResponseData.PreviewIds is not None and \
                    len(previewOrderResponse.PreviewOrderResponseData.PreviewIds) != 0:                
                    
                    # Place order using input of the preview.
                    placeOrderResponse = entryInput.Order.PlaceOrderEQ(accountIdKey= entryInput.ETradeSettings.AccountIdKey, 
                        previewOrderInput = previewOrderInput,
                        previewIds = previewOrderResponse.PreviewOrderResponseData.PreviewIds,
                        accessToken= accessToken, 
                        accessTokenSecret= accessTokenSecret, 
                    )                
                    print(placeOrderResponse)

                    # If error, process error and continue.
                    if placeOrderResponse is not None and placeOrderResponse.Error is not None:
                        ProcessResponseError(placeOrderResponse.Error, entryInput)
                        accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                        continue

                    # Process message and continue if required.
                    if(placeOrderResponse.Messages is not None and len(placeOrderResponse.Messages) != 0):
                        if(ProcessMessageError(placeOrderResponse.Messages, entryInput) is False):
                            continue

                    # Print Placed order details.
                    if placeOrderResponse is not None and placeOrderResponse.PlaceOrderResponseData is not None:
                        print("************Place Order Response Begin***********************")
                        print("Total Commission -> ", placeOrderResponse.PlaceOrderResponseData.TotalCommission)
                        print("Order Id -> ", placeOrderResponse.PlaceOrderResponseData.OrderId)
                        for orderId in placeOrderResponse.PlaceOrderResponseData.OrderIds:
                            print("orderId - >", orderId.OrderId)
                            placedOrderId = orderId.OrderId

                        orderDetails = placeOrderResponse.PlaceOrderResponseData.OrderDetails
                        for orderDetail in orderDetails:
                            print("Estimated commission -> ", orderDetail.EstimatedCommission)
                            print("Estimated Fees -> ", orderDetail.EstimatedFees)
                            instruments = orderDetail.Instruments
                            for instrument in instruments:
                                print("Symbol - Quantity -> ", instrument.Symbol, instrument.Quantity)
                                print("EstimatedCommission -> ", instrument.EstimatedCommission)
                                print("EstimatedFees -> ", instrument.EstimatedFees)
                            for message in orderDetail.Messages:
                                print("Message Description -> ", message.Description)
                                print("Message Code -> ", message.Code)
                                print("Message Type -> ", message.Type)
                        print("************Place Order Response End***********************")

                    # Cancel the placed order.
                    if placedOrderId != 0:
                        cancelOrderResponse:CancelOrderResponse = entryInput.Order.CancelOrder(entryInput.ETradeSettings.AccountIdKey, placedOrderId, 
                                    accessToken = accessToken, accessTokenSecret=accessTokenSecret)
                        print(cancelOrderResponse)

                        # Process error and continue.
                        if cancelOrderResponse is not None and cancelOrderResponse.Error is not None:
                            ProcessResponseError(cancelOrderResponse.Error, entryInput)
                            accessToken, accessTokenSecret, dateTimeObj = entryInput.Configuration.GetLatestETradeAccessKeyDetails()
                            continue
                        
                        # Process messages and continue if required.
                        if(cancelOrderResponse.Messages is not None and len(cancelOrderResponse.Messages) != 0):
                            if(ProcessMessageError(cancelOrderResponse.Messages, entryInput) is False):
                                continue

                        if cancelOrderResponse.OrderId != 0:
                            print("Cancelled Order Id -> ", cancelOrderResponse.OrderId)
                """
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
            # Internet connection issue, we can try again.
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
    """Sample program showing how to preview and place an Order.
    """
    entryInput = EntryOrderInput()
    DoOrder(entryInput)
