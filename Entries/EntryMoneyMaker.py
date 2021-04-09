import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Add the Parent path of the Entries folder to the system path.
# Need to find out if there is a better way of doing this.
sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.CancelOrderResponse import CancelOrderResponse
from BusinessModels.Error import Error
from BusinessModels.FilteringAndPagingParams import (
    OrdersFilteringAndPagingParams, PortfolioFilteringAndPagingParams)
from BusinessModels.Message import Message
from BusinessModels.OrderDetails import Instrument, OrderDetail
from BusinessModels.OrderInfo import OrderInfo
from BusinessModels.OrdersResponse import Order
from BusinessModels.PortfolioResponse import PortfolioPosition
from BusinessModels.PreviewOrderInput import PreviewOrderInput
from Exceptions.MessageError import MessageError
from Exceptions.ResponseError import ResponseError
from requests.exceptions import ConnectionError

from Entries.EntryHelpers.ErrorHandlingHelpers import \
    ProcessMessageError as ProcessMessageError
from Entries.EntryHelpers.ErrorHandlingHelpers import \
    ProcessResponseError as ProcessResponseError
from Entries.EntryHelpers.ManageOrdersHelpers import ManageOrdersHelpers
from Entries.EntryInputs.EntryMoneyMakerInput import EntryMoneyMakerInput


class MoneyMaker:
    """ Main class which tries to help us make money. Only EQ type orders are supported.
         
        Attributes:

        MoneyMakerInput: EntryMoneyMakerInput - Input to the MoneyMaker. Contains most of the 
        required objects.

        ManageOrdersHelpers:ManageOrdersHelpers - Methods related to the trading algorithm are available
        in this class.

        Methods:

        LogMessage - Logs the message passed using the Logger present in the Entry input.

        MoneyMakerProcessResponseError - Processes the API response error.

        MoneyMakerProcessMessageError - Processes the API response messages.

        OrderInput - Builds the order input.

        AddCommissionToSellOrder - Calculates the commission and updates the sell price accordingly.

        CalculateStockItemOrders - Calculates and generates the final orders to place.

        DoMakeMoney - Tries to make money following the below process.
            General steps are:
            - Gets the portfolio items.
            - Gets the active stock items.
            - For each stock item.
                - Get the available orders if any.
                - Calculate possible orders using the portfolio quantity and algorithm.
                - Compare available orders with calculated possible orders.
                    - If both orders are same then move to next stock item.
                    - If orders are different. Cancel all existing orders and place the possible caculated orders.
                    - Thats it - Sweet and Simple.
                - Move to next stock item.
            Repeat the above process after a fixed interval.
        
    """

    def __init__(self, entryInput:EntryMoneyMakerInput, manageOrdersHelpers:ManageOrdersHelpers):
        self.MoneyMakerInput = entryInput
        self.ManageOrdersHelpers = manageOrdersHelpers

    def LogMessage(self, message:str, isError:bool = False, isUser:bool = False): 
        """ Logs and/or prints the message using the MoneyMakerInput.LogMessage method.

            Parameters:

            message:str - Message to log.

            isError:bool - Is this error message?

            isUser:bool - Should we present the message to the User.
        """   
        self.MoneyMakerInput.LogMessage(self.MoneyMakerInput.MoneyMakerLogger, message, isError, isUser)

    def MoneyMakerProcessResponseError(self, error:Error):
        """ Process the response error.
            Uses the ProcessResponseError method to process the Error.

            error:Error - Error object.
        """
        self.LogMessage(f"Error status code - {error.ResponseStatusCode}", True, True)
        self.LogMessage(f"Error code - {error.Code}", True, True)
        self.LogMessage(f"Error message - {error.Message}", True, True)
        ProcessResponseError(error, self.MoneyMakerInput)

    def MoneyMakerProcessMessageError(self, messages:List[Message]):
        """ Process the response messages.
            Uses the ProcessMessageError method to process the Error.

            messages:List[Message] - List of response messages.
        """
        for message in messages:   
            if(message.Code in self.MoneyMakerInput.ETradeSettings.DangerErrorCodes):
                self.LogMessage(f"Message type - {message.Type.name}", True, True)
                self.LogMessage(f"Message Code - {message.Code}", True, True)
                self.LogMessage(f"Message Description - {message.Description}", True, True)
        ProcessMessageError(messages, self.MoneyMakerInput)

    def OrderInput(self, symbol:str, orderAction:str, limitPrice:float, quantity:int) -> PreviewOrderInput:
        """ Creates the input for the preview order.
            OrderType is fixed to "EQ"
            PriceType is fixed to "LIMIT"
            OrderTerm is fixed to "GOOD_UNTIL_CANCEL"
            MarketSession is fixed to "REGULAR"
            AllOrNone is fixed to "true"

            Parameters:

            symbol:str - Stock symbol.

            orderAction:str - BUY or SELL

            limitPrice:float - Price at which to place the limit order.

            quantity:int - Order quantity.

        """
        previewOrderInput = PreviewOrderInput()

        # Unique ClientOrderId
        previewOrderInput.ClientOrderId = "O" + str(time.time()).replace(".", "") 
        previewOrderInput.OrderType = "EQ"
        previewOrderInput.Order = []

        # Build the order detail.
        orderDetail = OrderDetail()
        # "false"
        orderDetail.AllOrNone = "true"
        orderDetail.PriceType = "LIMIT"
        # GOOD_FOR_DAY
        # GOOD_UNTIL_CANCEL
        orderDetail.OrderTerm = "GOOD_UNTIL_CANCEL"
        # REGULAR
        # EXTENDED
        orderDetail.MarketSession = "REGULAR"
        orderDetail.StopPrice = ""
        orderDetail.LimitPrice = limitPrice
        orderDetail.Instruments = []

        # Build the Instrument.
        instrument = Instrument()
        instrument.SecurityType = "EQ"
        instrument.Symbol = symbol
        instrument.OrderAction = orderAction
        instrument.QuantityType = "QUANTITY"
        instrument.Quantity = quantity

        orderDetail.Instruments.append(instrument)
        previewOrderInput.Order.append(orderDetail)

        return previewOrderInput

    def AddCommissionToSellOrder(self, orderInfo:OrderInfo, activeStockItem:ActiveStockItem):
        """ Add commission to the Sell Order based on the CommisionType in the settings.

            CommissionType = 1 - commission is fixed value.
            CommissionType = 2 - commission is percentage.

            Parameters:

            orderInfo:OrderInfo - Order to which to add commission.

            activeStockItem:ActiveStockItem - active stock item used to get the Buy price for the given Sell price.

        """

        # Not a sell order.
        if(orderInfo.IsSell is False):
            return
        
        # If commission type is FIXED value.
        if(self.MoneyMakerInput.ETradeSettings.CommissionType == 1):
            # Add the share of Buy commission to the LimitPrice.
            if(self.MoneyMakerInput.ETradeSettings.BuyCommission > 0):
                orderInfo.LimitPrice = round(orderInfo.LimitPrice + (self.MoneyMakerInput.ETradeSettings.BuyCommission / orderInfo.Quantity), self.MoneyMakerInput.Settings.FloatRoundPrecision)

            # Add the share of Sell commission to the LimitPrice.
            if(self.MoneyMakerInput.ETradeSettings.SellCommission > 0):
                orderInfo.LimitPrice = round(orderInfo.LimitPrice + (self.MoneyMakerInput.ETradeSettings.SellCommission / orderInfo.Quantity), self.MoneyMakerInput.Settings.FloatRoundPrecision)

        # If the commission type is PERCENTAGE.
        if(self.MoneyMakerInput.ETradeSettings.CommissionType == 2):
            tempCommission = 0
            # Add Buy commission percentage to the tempCommission.
            if(self.MoneyMakerInput.ETradeSettings.BuyCommission > 0):
                buyPrice = self.ManageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, orderInfo.LimitPrice)
                tempCommission = tempCommission + round((buyPrice * self.MoneyMakerInput.ETradeSettings.BuyCommission * 0.01) / orderInfo.Quantity, self.MoneyMakerInput.Settings.FloatRoundPrecision)

            # Add Sell commission percentage to the tempCommission.
            if(self.MoneyMakerInput.ETradeSettings.SellCommission > 0):
                tempCommission = tempCommission + round((orderInfo.LimitPrice * self.MoneyMakerInput.ETradeSettings.SellCommission * 0.01) / orderInfo.Quantity, self.MoneyMakerInput.Settings.FloatRoundPrecision)

            # Add commission to the LimitPrice.
            orderInfo.LimitPrice = orderInfo.LimitPrice + tempCommission

    def CalculateStockItemOrders(self, activeStockItem:ActiveStockItem,  
                                openOrders:List[Order], portfolioPosition:PortfolioPosition) -> Tuple[List[OrderInfo], List[OrderInfo]]:
        """ Calculate the possible Orders for a stock item based on the current orders and portfolio quantity.

            Parameters:

            activeStockItem:ActiveStockItem - Active stock item.

            openOrders:List[Order] - Open orders of the stock item.

            portfolioPosition:PortfolioPosition - Portfolio details of the stock item.

            Returns:

            Tuple[List[OrderInfo], List[OrderInfo]] - [Orders to Place, Orders to Cancel]

        """

        # Get portfolio quantity.
        portfolioPositionQuantity:int = portfolioPosition.Quantity

        # Get possible limit orders.
        limitOrders = self.ManageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioPositionQuantity)

        # Add commission.
        for orderInfo in limitOrders:
            self.AddCommissionToSellOrder(orderInfo, activeStockItem)

        # Calculated quantity from open orders.
        calculatedQuantity:int = 0

        skipOrder:bool = False

        openLimitOrders:List[OrderInfo] = []
        # For each open Order.
        for orderObj in openOrders:
            for orderDetail in orderObj.OrderDetails:
                # Get the instruments.
                for instrument in orderDetail.Instruments:                    
                    inst:Instrument = instrument     
                    # If OPEN and BUY
                    if inst.Symbol.upper() == activeStockItem.Symbol.upper() and orderDetail.Status == "OPEN" and \
                        inst.OrderAction == "BUY":
                        # There is a chance of partial fill.
                        calculatedQuantity = calculatedQuantity + inst.FilledQuantity
                        openLimitOrders.append(OrderInfo(orderObj.OrderId, inst.Symbol, orderDetail.LimitPrice, 
                        inst.OrderedQuantity, inst.FilledQuantity != 0, False))
                        # In case of ONE_TRIGGERS_OTHER orders. First BUY needs to be completed before
                        # SELL is started. We are not dealing with ONE_TRIGGERS_OTHER type orders.
                        # Only one instrument will be present for Order in our application.
                        # So the skipOrder is not required actually. No harm.
                        skipOrder = True 
                        break      
                    # If OPEN and SELL.            
                    elif inst.Symbol.upper() == activeStockItem.Symbol.upper() and orderDetail.Status == "OPEN" and \
                        inst.OrderAction == "SELL":
                        # There is a chance of partial fill.
                        calculatedQuantity = calculatedQuantity + inst.OrderedQuantity - inst.FilledQuantity
                        openLimitOrders.append(OrderInfo(orderObj.OrderId, inst.Symbol, orderDetail.LimitPrice, 
                        inst.OrderedQuantity, inst.FilledQuantity != 0, True))

                # This is not required. No harm.
                if skipOrder is True:
                    skipOrder = False
                    break

        if(len(openLimitOrders) != len(openOrders)):
            self.LogMessage(f"Number of open limit orders should be same as that of open orders.", True, True)
            self.LogMessage("Aborting the application.", True, True)
            raise Exception("Fatal Error.")

        # If no open orders. 
        if len(openLimitOrders) == 0:
            return limitOrders, []
        
        # If open orders length is not same as possible orders.
        if(len(openLimitOrders) != len(limitOrders)):
            return limitOrders, openLimitOrders
        
        limitOrders.sort(key= lambda x:x.LimitPrice, reverse=True)

        # Check if the orders match exactly or not.
        for limitOrder in limitOrders:
            found = False
            for openLimitOrder in openLimitOrders:
                if limitOrder.Symbol.upper() == openLimitOrder.Symbol.upper() and \
                    limitOrder.LimitPrice == openLimitOrder.LimitPrice and \
                    limitOrder.Quantity == openLimitOrder.Quantity and \
                    limitOrder.IsPartialFilled == openLimitOrder.IsPartialFilled and \
                    limitOrder.IsSell == openLimitOrder.IsSell:
                    found = True
                    break
            # If any order does not match.
            if found is False:
                return limitOrders, openLimitOrders

        # Everything matches so no change to the orders of the stock item.
        return [],[]

        """
        for orderObj in openOrders:
            for orderDetail in orderObj.OrderDetails:
                if(orderDetail.AllOrNone == False):
                    return limitOrders, openLimitOrders
        
        openBuyCount = 0
        for openLimitOrder in openLimitOrders:
            if openLimitOrder.IsSell == False:
                openBuyCount = openBuyCount + 1

        if openBuyCount != buyOpenCountConst:
            calculatedQuantity = calculatedQuantity + activeStockItem.Quantity * (buyOpenCountConst-openBuyCount)

        # If calculated quantity is not same as portfolio quality. We shall
        # take care of this in the next cycle.
        if calculatedQuantity != portfolioPosition.Quantity:
            return [],[]
        
        finalLimitOrders:List[OrderStatusInfo] = []
        found:bool = False

        for limitOrder in limitOrders:
            found = False
            for openLimitOrder in openLimitOrders:
                if limitOrder.LimitPrice == openLimitOrder.LimitPrice and \
                    limitOrder.IsSell == openLimitOrder.IsSell:
                    finalLimitOrders.append(openLimitOrder)
                    found = True
                    break
            if found == False:
                finalLimitOrders.append(limitOrder)

        cancelOrders:List[OrderStatusInfo] = []
        for openLimitOrder in openLimitOrders:
            found = False
            for finalLimitOrder in finalLimitOrders:
                if finalLimitOrder.OrderId == openLimitOrder.OrderId:
                    found = True
                    break
            if found == False:
                cancelOrders.append(openLimitOrder)

        finalLimitOrders.sort(key= lambda x:x.LimitPrice, reverse=True)
        cancelOrders.sort(key= lambda x:x.LimitPrice)
        return finalLimitOrders, cancelOrders
        """

    def DoMakeMoney(self):
        """ Tries to make money following the below process.
            General steps are:
            - Gets the portfolio items.
            - Gets the active stock items.
            - For each stock item.
                - Get the available orders if any.
                - Calculate possible orders using the portfolio quantity and algorithm.
                - Compare available orders with calculated possible orders.
                    - If both orders are same then move to next stock item.
                    - If orders are different. Cancel all existing orders and place the possible caculated orders.
                    - Thats it - Sweet and Simple.
                - Move to next stock item.
            Repeat the above process after a fixed interval.
        """
        proceed = True
        while True:
                    
            # Get the latest Access Keys and update the Input with the latest keys.
            # We can move the updation part to the EntryInput itself, but it's ok.
            accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
            self.MoneyMakerInput.InputModel.AccessToken = accessToken
            self.MoneyMakerInput.InputModel.AccessTokenSecret = accessTokenSecret
            self.MoneyMakerInput.InputModel.AccessTokenDateTime = dateTimeObj
            self.MoneyMakerInput.Auth.inputModel = self.MoneyMakerInput.InputModel
            self.MoneyMakerInput.Account.inputModel = self.MoneyMakerInput.InputModel
            self.MoneyMakerInput.Order.inputModel = self.MoneyMakerInput.InputModel

            try:
                
                # Get the portfolio items.
                portfolioFilteringAndPagingParams = PortfolioFilteringAndPagingParams(pageSize=100, pageNumber=1)
                portfolioFilteringAndPagingParams.ApplyFilterAndReturnAll = True
                portfolioResponse = self.MoneyMakerInput.Account.Portfolio(self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                                                    accessToken = accessToken, 
                                                    accessTokenSecret = accessTokenSecret,
                                                    filteringAndPagingParams= portfolioFilteringAndPagingParams
                                                    )

                # Handle portfolio response error if any.
                if(portfolioResponse.Error is not None and portfolioResponse.Error.ResponseStatusCode != ""):
                    # Process error, get latest tokens and continue.
                    self.MoneyMakerProcessResponseError(portfolioResponse.Error)
                    accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
                    continue                

                if self.MoneyMakerInput.ActiveStockItems is not None and len(self.MoneyMakerInput.ActiveStockItems) != 0:
                    # For each active stock item in the system.
                    for activeStockIndex in range(len(self.MoneyMakerInput.ActiveStockItems)):                
                        orderFilteringAndPagingParams = OrdersFilteringAndPagingParams()
                        orderFilteringAndPagingParams.PageSize = 100
                        # orderFilteringAndPagingParams.Params["fromDate"] = "09012020"
                        # orderFilteringAndPagingParams.Params["toDate"] = "09012020"
                        orderFilteringAndPagingParams.Params["symbol"] = self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol
                        orderFilteringAndPagingParams.Params["status"] = "OPEN"
                        orderFilteringAndPagingParams.Params["securityType"] = "EQ"
                        orderFilteringAndPagingParams.ApplyFilterAndReturnAll = True

                        # Get the OPEN Orders.
                        ordersResponse = self.MoneyMakerInput.Order.Orders(accountIdKey= self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                            accessToken= accessToken, 
                            accessTokenSecret= accessTokenSecret, 
                            filteringAndPagingParams= orderFilteringAndPagingParams)
                    
                        # Handle orders response error.
                        if(ordersResponse.Error is not None and ordersResponse.Error.ResponseStatusCode != ""):
                            self.MoneyMakerProcessResponseError(ordersResponse.Error)
                            accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
                            continue

                        # Handle response messages.
                        if(ordersResponse.Messages is not None and len(ordersResponse.Messages) != 0):
                            if(self.MoneyMakerProcessMessageError(ordersResponse.Messages) is False):
                                continue
    
                        # Get the portfolio position for the given active stock.
                        # It may not be present in the portfolio.
                        dummySymbol = "XXXXABCD"
                        portfolioPosition:PortfolioPosition = PortfolioPosition(symbol=dummySymbol)
                        if portfolioResponse.AccountPortfolios is not None and \
                            len(portfolioResponse.AccountPortfolios) != 0 and \
                            portfolioResponse.AccountPortfolios[0].PortfolioPositions is not None and \
                            len(portfolioResponse.AccountPortfolios[0].PortfolioPositions) != 0:
                            portfolioPosition = next((item for item in portfolioResponse.AccountPortfolios[0].PortfolioPositions if item.Symbol.upper() == self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol.upper()), portfolioPosition)

                        # If not present.
                        if(portfolioPosition.Symbol == dummySymbol):
                            # Set the Symbol
                            portfolioPosition.Symbol = self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol
                            # Set the Quantity to 0 because quantity is initialized to Settings.UnfilledValue in the constructor.
                            portfolioPosition.Quantity = 0
                        # If present in the portfolio. Make sure quantity is set by the API.
                        elif(portfolioPosition.Quantity == self.MoneyMakerInput.Settings.UnfilledValue) or (portfolioPosition.Quantity <= 0):
                            self.LogMessage(f"Something changed - Portfolio Quantity for {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol} received from API is not suppossed to be {portfolioPosition.Quantity}", True, True)
                            self.LogMessage("Aborting the application.", True, True)
                            raise Exception("Fatal Error.")
                                        
                        limitOrders:List[OrderInfo]
                        cancelOrders:List[OrderInfo]

                        # Get the orders to Place and orders to Cancel.
                        limitOrders, cancelOrders = self.CalculateStockItemOrders(self.MoneyMakerInput.ActiveStockItems[activeStockIndex], ordersResponse.Orders, 
                                                        portfolioPosition)

                        # Sort the LimitOrders. High price orders are placed first.
                        limitOrders.sort(key= lambda x:x.LimitPrice, reverse=True)

                        # Low price orders are cancelled first.
                        cancelOrders.sort(key= lambda x:x.LimitPrice)

                        self.LogMessage(f"StartPrice -> {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].StartPrice}", False, False)
                        self.LogMessage(f"Limit Orders -> {limitOrders}", False, False)
                        self.LogMessage(f"Cancel Orders -> {cancelOrders}", False, False)

                        # In one cycle cancel the orders and in the next cycle place the orders.
                        # Reason for this approach is, there is a delay when orders are cancelled.
                        if(len(cancelOrders) != 0):
                            logMessage = f"Processing cancel orders of {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol} - {cancelOrders}" 
                            self.LogMessage(logMessage, False, True)
                            for cancelOrder in cancelOrders:
                                # Cancel order.
                                cancelOrderResponse:CancelOrderResponse = self.MoneyMakerInput.Order.CancelOrder(accountIdKey= self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                                        orderId = cancelOrder.OrderId, accessToken = accessToken, accessTokenSecret=accessTokenSecret)
                                
                                # Process cancel response error.
                                if(cancelOrderResponse.Error is not None and cancelOrderResponse.Error.ResponseStatusCode != ""):
                                    self.MoneyMakerProcessResponseError(cancelOrderResponse.Error)
                                    accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
                                    continue

                                # Process cancel response message.
                                if(cancelOrderResponse.Messages is not None and len(cancelOrderResponse.Messages) != 0):
                                    if(self.MoneyMakerProcessMessageError(cancelOrderResponse.Messages) is False):
                                        continue

                            # Get the orders again to verify if they are cancelled or not.
                            ordersResponse = self.MoneyMakerInput.Order.Orders(accountIdKey= self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                                accessToken= accessToken, 
                                accessTokenSecret= accessTokenSecret, 
                                filteringAndPagingParams= orderFilteringAndPagingParams) 

                            # Process orders response error.
                            if(ordersResponse.Error is not None and ordersResponse.Error.ResponseStatusCode != ""):
                                self.MoneyMakerProcessResponseError(ordersResponse.Error)
                                accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
                                continue

                            # Process orders response messages.
                            if(ordersResponse.Messages is not None and len(ordersResponse.Messages) != 0):
                                if(self.MoneyMakerProcessMessageError(ordersResponse.Messages) is False):
                                    continue

                            # Are all orders cancelled?                
                            if(ordersResponse.Orders is not None and len(ordersResponse.Orders) == 0):
                                logMessage = f"All existing orders of {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol} are cancelled successfully."
                                self.LogMessage(logMessage, False, True)
                            else:
                                logMessage = f"Unable to cancel all the existing orders of {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol}."
                                self.LogMessage(logMessage, True, True)
                                continue                                                
                        
                            # In either case we will place orders in the next cycle.
                            # We are not in a hurry :)
                        else:
                            logMessage = f"Processing place limit orders of {self.MoneyMakerInput.ActiveStockItems[activeStockIndex].Symbol} - {limitOrders}"
                            self.LogMessage(logMessage, False, True)

                            # Preview and Place orders.
                            for limitOrder in limitOrders:
                                # If existing order.
                                if(limitOrder.OrderId > 0):
                                    continue
                                logMessage = f"Processing place limit order - {limitOrder}"
                                self.LogMessage(logMessage, False, True)
                                orderAction:str = "BUY"
                                if(limitOrder.IsSell):
                                    orderAction = "SELL"
                                
                                # Generate order input.
                                orderData = self.OrderInput(limitOrder.Symbol,
                                                    orderAction, limitOrder.LimitPrice, limitOrder.Quantity)
                                
                                # Preview order.
                                previewOrderResponse = self.MoneyMakerInput.Order.PreviewOrderEQ(accountIdKey= self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                                                        previewOrderInput = orderData,
                                                        accessToken= accessToken, 
                                                        accessTokenSecret= accessTokenSecret, 
                                                    )

                                # Handle preview response error.
                                if(previewOrderResponse.Error is not None and previewOrderResponse.Error.ResponseStatusCode != ""):
                                    self.MoneyMakerProcessResponseError(previewOrderResponse.Error)
                                    accessToken, accessTokenSecret, dateTimeObj = self.MoneyMakerInput.Configuration.GetLatestETradeAccessKeyDetails()
                                    continue
                                    
                                # Handle preview response messages.
                                if(previewOrderResponse.Messages is not None and len(previewOrderResponse.Messages) != 0):
                                    if(self.MoneyMakerProcessMessageError(previewOrderResponse.Messages) is False):
                                        continue

                                # The process to validate the Preview and Place order responses is, there are some
                                # data fields which should to be populated by the API. I am verifying if these
                                # fields are populated by the API or not.
                                # I am also verifying some values like total order value.
                                # Commission should not be more than maxCommission.
                                # In future if something changes with the API we have to change the validations done on
                                # the Preview and Place responses.
                                # The reason, I am doing it this way is to make sure that nothing goes wrong.
                                # It is OK if we are not able to place the Order. I am trying to avoid placing a bad order.                                

                                isValid = False

                                # Calculate total value of the Order.
                                totalValue = round(limitOrder.LimitPrice * limitOrder.Quantity, self.MoneyMakerInput.Settings.FloatRoundPrecision)
                                unfilledCommissionFee = self.MoneyMakerInput.Settings.UnfilledCommissionOrFee
                                unfilledValue = self.MoneyMakerInput.Settings.UnfilledValue        
                                maxCommission = self.MoneyMakerInput.Settings.MaxCommission

                                if previewOrderResponse is not None and previewOrderResponse.PreviewOrderResponseData is not None:
                                    self.LogMessage(f"Total Commission -> {previewOrderResponse.PreviewOrderResponseData.TotalCommission}", False, False)
                                    self.LogMessage(f"Total Order Value -> {previewOrderResponse.PreviewOrderResponseData.TotalOrderValue}", False, False)
                                    # TotalCommission is not suppossed to be filled by the API.
                                    if previewOrderResponse.PreviewOrderResponseData.TotalCommission != unfilledCommissionFee:
                                        logMessage = f"Something changed - TotalCommission is suppossed to be {unfilledCommissionFee}"
                                        self.LogMessage(logMessage, True, True)
                                        logMessage = f"Aborting place order."
                                        self.LogMessage(logMessage, True, True)                                
                                        raise Exception("Fatal Error.")
                                    # TotalOrderValue should be same as totalValue.
                                    if orderAction == "BUY" and \
                                        (totalValue - previewOrderResponse.PreviewOrderResponseData.TotalOrderValue != 0):
                                        self.LogMessage(f"Something changed - TotalOrderValue is suppossed to be {totalValue}, received value is {previewOrderResponse.PreviewOrderResponseData.TotalOrderValue}", True, True)
                                        self.LogMessage("Aborting place order.", True, True)
                                        raise Exception("Fatal Error.")
                                    # In case of SELL TotalOrderValue is negative. Commision charged should not be greater than maxCommission.
                                    if orderAction == "SELL" and \
                                        (totalValue + previewOrderResponse.PreviewOrderResponseData.TotalOrderValue > maxCommission):
                                        self.LogMessage(f"Something changed - Too much commission - {totalValue + previewOrderResponse.PreviewOrderResponseData.TotalOrderValue}.", True, True)
                                        self.LogMessage(f"Aborting place order.", True, True)
                                        raise Exception("Fatal Error.")
                                    orderDetails:List[OrderDetail] = previewOrderResponse.PreviewOrderResponseData.OrderDetails
                                    for orderDetail in orderDetails:
                                        self.LogMessage(f"Estimated commission -> {orderDetail.EstimatedCommission}")
                                        self.LogMessage(f"Estimated Fees -> {orderDetail.EstimatedFees}")
                                        self.LogMessage(f"Estimated Total Amount -> {orderDetail.EstimatedTotalAmount}")
                                        # EstimatedCommission should be 0. This may change in future.
                                        if(orderDetail.EstimatedCommission != 0):
                                            self.LogMessage(f"Something changed, commission is suppossed to be 0, received commission {orderDetail.EstimatedCommission}", True, True)
                                            self.LogMessage(f"Aborting place order.", True, True)
                                            raise Exception("Fatal Error.")
                                        # EstimatedFees is not supposed to be set by the API.
                                        if(orderDetail.EstimatedFees != unfilledCommissionFee):
                                            self.LogMessage(f"Something changed, fees is suppossed to be {unfilledCommissionFee}, received fees value is {orderDetail.EstimatedFees}", True, True)
                                            self.LogMessage(f"Aborting place order.", True, True)
                                            raise Exception("Fatal Error.")
                                        # When BUY EstimatedTotalAmount should be same as totalValue.
                                        if orderAction == "BUY" and \
                                            (totalValue - orderDetail.EstimatedTotalAmount != 0):
                                            self.LogMessage(f"Something changed - EstimatedTotalAmount is suppossed to be {totalValue}, received total amount is {orderDetail.EstimatedTotalAmount}", True, True)
                                            self.LogMessage(f"Aborting place order.", True, True)
                                            raise Exception("Fatal Error.")
                                        # When SELL EstimatedTotalAmount is negative. Commission charged cannot be more than maxCommission.
                                        if orderAction == "SELL" and \
                                            (totalValue + orderDetail.EstimatedTotalAmount > maxCommission):
                                            self.LogMessage(f"Something changed - Too much commission - {totalValue + orderDetail.EstimatedTotalAmount}", True, True)
                                            self.LogMessage(f"Aborting place order.", True, True)
                                            raise Exception("Fatal Error.")
                                        instruments:List[Instrument] = orderDetail.Instruments
                                        for instrument in instruments:
                                            self.LogMessage(f"Symbol - Quantity -> {instrument.Symbol}, {instrument.Quantity}")
                                            self.LogMessage(f"EstimatedCommission -> {instrument.EstimatedCommission}")
                                            self.LogMessage(f"EstimatedFees -> {instrument.EstimatedFees}")
                                            # EstimatedCommission is not suppossed to be set by the API.
                                            if(instrument.EstimatedCommission != unfilledCommissionFee):
                                                self.LogMessage(f"Something changed, estimated commission is suppossed to be {unfilledCommissionFee}, received commission is {instrument.EstimatedCommission}", True, True)
                                                self.LogMessage(f"Aborting place order.", True, True)
                                                raise Exception("Fatal Error.")
                                            # EstimatedFees is not suppossed to be set by the API.
                                            if(instrument.EstimatedFees != unfilledCommissionFee):
                                                self.LogMessage(f"Something changed, estimated fees is suppossed to be {unfilledCommissionFee}, received fees is {instrument.EstimatedFees}", True, True)
                                                self.LogMessage(f"Aborting place order.", True, True)
                                                raise Exception("Fatal Error.")

                                        # Handle orderDetail messages.
                                        if(orderDetail.Messages is not None and len(orderDetail.Messages) != 0):
                                            if(self.MoneyMakerProcessMessageError(orderDetail.Messages) is False):
                                                continue
                                        isValid = True

                                # If isValid is false. Something went wrong.
                                if isValid is False:
                                    self.LogMessage(f"Failed to place {orderAction} Order {limitOrder.Symbol} at {limitOrder.LimitPrice}", True, True)  
                                    continue

                                # Place the order using the input from preview and previewIds.
                                placeOrderResponse = self.MoneyMakerInput.Order.PlaceOrderEQ(accountIdKey= self.MoneyMakerInput.ETradeSettings.AccountIdKey, 
                                                    previewOrderInput = orderData,
                                                    previewIds = previewOrderResponse.PreviewOrderResponseData.PreviewIds,
                                                    accessToken= accessToken, 
                                                    accessTokenSecret= accessTokenSecret
                                                    )      

                                # Handle place order response errors.
                                if(placeOrderResponse.Error is not None and placeOrderResponse.Error.ResponseStatusCode != ""):
                                    self.MoneyMakerProcessResponseError(placeOrderResponse.Error)
                                    continue

                                # Handle place order message errors.
                                if(placeOrderResponse.Messages is not None and len(placeOrderResponse.Messages) != 0):
                                    if(self.MoneyMakerProcessMessageError(placeOrderResponse.Messages) is False):
                                        continue

                                isValid = False
                                if placeOrderResponse is not None and placeOrderResponse.PlaceOrderResponseData is not None:  
                                    self.LogMessage(f"Total Commission -> {placeOrderResponse.PlaceOrderResponseData.TotalCommission}")
                                    self.LogMessage(f"Total Order Value -> {placeOrderResponse.PlaceOrderResponseData.TotalOrderValue}")

                                    # Get the OrderId of the placed Order.
                                    placedOrderId = placeOrderResponse.PlaceOrderResponseData.OrderId
                                    if placeOrderResponse.PlaceOrderResponseData.OrderId == 0 and \
                                            placeOrderResponse.PlaceOrderResponseData.OrderIds is not None and \
                                            len(placeOrderResponse.PlaceOrderResponseData.OrderIds) != 0:
                                        placedOrderId = placeOrderResponse.PlaceOrderResponseData.OrderIds[0].OrderId
                                    
                                    # TotalCommission is not suppossed to be filled by API.
                                    if placeOrderResponse.PlaceOrderResponseData.TotalCommission != unfilledCommissionFee:
                                        self.LogMessage(f"Something changed - TotalCommission is suppossed to be {unfilledCommissionFee}, received commission is {placeOrderResponse.PlaceOrderResponseData.TotalCommission}", True, True)
                                        self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                        raise Exception("Fatal Error.")
                                    # TotalOrderValue is not suppossed to be filled by API.
                                    if placeOrderResponse.PlaceOrderResponseData.TotalOrderValue != unfilledValue:
                                        self.LogMessage(f"Something changed - TotalOrderValue is suppossed to be {unfilledValue}, received value is {placeOrderResponse.PlaceOrderResponseData.TotalOrderValue}", True, True)
                                        self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                        raise Exception("Fatal Error.")
                                    orderDetails:List[OrderDetail] = placeOrderResponse.PlaceOrderResponseData.OrderDetails
                                    for orderDetail in orderDetails:
                                        self.LogMessage(f"Estimated commission -> {orderDetail.EstimatedCommission}")
                                        self.LogMessage(f"Estimated Fees -> {orderDetail.EstimatedFees}")
                                        self.LogMessage(f"Estimated Total Amount -> {orderDetail.EstimatedTotalAmount}")
                                        # EstimatedCommission is suppossed to be zero.
                                        if(orderDetail.EstimatedCommission != 0):
                                            self.LogMessage(f"Something changed, commission is suppossed to be 0, received value is {orderDetail.EstimatedCommission}", True, True)
                                            self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                            raise Exception("Fatal Error.")
                                        # EstimatedFees is not suppossed to be filled by the API.
                                        if(orderDetail.EstimatedFees != unfilledCommissionFee):
                                            self.LogMessage(f"Something changed, fees is suppossed to be {unfilledCommissionFee}, received value is {orderDetail.EstimatedFees}", True, True)
                                            self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                            raise Exception("Fatal Error.")
                                        # If BUY totalValue should be same as EstimatedTotalAmount.
                                        if orderAction == "BUY" and \
                                            (totalValue - orderDetail.EstimatedTotalAmount != 0):
                                            self.LogMessage(f"Something changed - EstimatedTotalAmount is suppossed to be {totalValue}, received value is {orderDetail.EstimatedTotalAmount}", True, True)
                                            self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                            raise Exception("Fatal Error.")
                                        # If SELL EstimatedTotalAmount is negative. Commission charged cannot be more than maxCommission.
                                        if orderAction == "SELL" and \
                                            (totalValue + orderDetail.EstimatedTotalAmount > maxCommission):
                                            self.LogMessage(f"Something changed - Too much commission - {totalValue + orderDetail.EstimatedTotalAmount}", True, True)
                                            self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.",True, True)
                                            raise Exception("Fatal Error.")
                                        instruments:List[Instrument] = orderDetail.Instruments
                                        for instrument in instruments:
                                            self.LogMessage(f"Symbol - Quantity -> {instrument.Symbol}, {instrument.Quantity}")
                                            self.LogMessage(f"EstimatedCommission -> {instrument.EstimatedCommission}")
                                            self.LogMessage(f"EstimatedFees -> {instrument.EstimatedFees}")
                                            # EstimatedCommission is not suppossed to be filled by the API.
                                            if(instrument.EstimatedCommission != unfilledCommissionFee):
                                                self.LogMessage(f"Something changed, estimated commission is suppossed to be {unfilledCommissionFee}, received value is {instrument.EstimatedCommission}", True, True)
                                                self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                                raise Exception("Fatal Error.")
                                            # EstimatedFees is not suppossed to be filled by the API.
                                            if(instrument.EstimatedFees != unfilledCommissionFee):
                                                self.LogMessage(f"Something changed, estimated fees is suppossed to be {unfilledCommissionFee}, received value is {instrument.EstimatedFees}", True, True)
                                                self.LogMessage(f"Critical - Order is already placed. Order Id is  {placedOrderId}.", True, True)
                                                raise Exception("Fatal Error.")

                                        # Handle orderDetail messages.
                                        if(orderDetail.Messages is not None and len(orderDetail.Messages) != 0):
                                            if(self.MoneyMakerProcessMessageError(orderDetail.Messages) is False):
                                                continue

                                        isValid = True

                                # isValid is false meaning something went wrong.
                                if isValid is False:
                                    self.LogMessage(f"Failed to place {orderAction} Order {limitOrder.Symbol} at {limitOrder.LimitPrice}", True, True)  
                                    continue

                                # We are here, all is well.
                                self.LogMessage(f"Placed {orderAction} Order {limitOrder.Symbol} at {limitOrder.LimitPrice}", True, True)  
                                        
            except MessageError as message:        
                self.LogMessage(self.MoneyMakerInput.Strings.UnexpectedError.format(message.Message.Type.name), True, True)
                self.LogMessage(self.MoneyMakerInput.Strings.UnexpectedError.format(message.Message.Code), True, True)
                self.LogMessage(self.MoneyMakerInput.Strings.UnexpectedError.format(message.Message.Description), True, True)
                proceed = False
            except ResponseError as error:
                self.LogMessage(f"Error status code - {error.Error.ResponseStatusCode}", True, True)
                self.LogMessage(f"Error code - {error.Error.Code}", True, True)
                self.LogMessage(f"Error message - {error.Error.Message}", True, True)
                proceed = False            
            except ConnectionError as connectionError:
                # Internet connection error, we can try again.
                self.LogMessage(f"Looks like internet connection issue - {connectionError}", True, True)
                proceed = True        
            except:
                self.LogMessage(self.MoneyMakerInput.Strings.UnexpectedError.format(sys.exc_info()), True, True)
                proceed = False

            # If proceed is False, something blocking happened, so we cannot continue.         
            if proceed is False:
                break
            
            # Get the current date and time for display.
            currentDateTime = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            print(f"{currentDateTime} - Waiting {self.MoneyMakerInput.Settings.CycleWaitTimeInSeconds} seconds before starting next cycle...")

            # Wait for time set in the Settings.
            time.sleep(self.MoneyMakerInput.Settings.CycleWaitTimeInSeconds)

            """
            exit = input("Please enter q to exit: ")
            if exit == 'q':
                break
            """
        
    
if __name__ == "__main__":
    """ Main driver program which tries to make money.
    """
    from BusinessModels.Settings import Settings
    manageOrdersHelpers:ManageOrdersHelpers = ManageOrdersHelpers(Settings())

    entryInput = EntryMoneyMakerInput()
    
    # Call DoMakeMoney on the MoneyMaker object.
    MoneyMaker(entryInput, manageOrdersHelpers).DoMakeMoney()
