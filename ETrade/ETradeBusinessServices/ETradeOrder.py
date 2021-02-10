import json
import sys
from typing import List
from urllib import parse

from BusinessModels.CancelOrderResponse import CancelOrderResponse
from BusinessModels.Context import Context
from BusinessModels.Error import Error
from BusinessModels.FilteringAndPagingParams import \
    OrdersFilteringAndPagingParams
from BusinessModels.Message import Message
from BusinessModels.OrderDetails import Instrument, OrderDetail
from BusinessModels.OrdersResponse import Event, Order, OrdersResponse
from BusinessModels.PlaceOrderResponse import (OrderId, PlaceOrderResponse,
                                               PlaceOrderResponseData)
from BusinessModels.PreviewOrderInput import PreviewOrderInput
from BusinessModels.PreviewOrderResponse import (PreviewId,
                                                 PreviewOrderResponse,
                                                 PreviewOrderResponseData)
from ETrade.ETradeBusinessModels.ETradeInputModel import ETradeInputModel
from ETrade.ETradeBusinessModels.ETradeSettings import ETradeSettings
from ETrade.ETradeBusinessServices.ETradeBusinessService import \
    ETradeBusinessService
from rauth import OAuth1Session
from Strings.FormatStringsBase import FormatStringsBase


class ETradeOrder(ETradeBusinessService):
    def __init__(self, inputModel: ETradeInputModel, settings: ETradeSettings, 
                    context: Context, strings: FormatStringsBase):
        if strings is None:
            raise ValueError(FormatStringsBase.InputStringsNone)
        self.strings = strings

        if inputModel is None:
            raise ValueError(self.strings.InputNone.format("inputModel"))
        if settings is None:
            raise ValueError(self.strings.InputNone.format("settings"))
        if context is None:
            raise ValueError(self.strings.InputNone.format("context"))

        self.inputModel: ETradeInputModel = inputModel
        self.context: Context = context
        self.settings: ETradeSettings = settings

        self.session = OAuth1Session(self.settings.ConsumerKey,
                        self.settings.ConsumerSecret,
                        self.inputModel.AccessToken,
                        self.inputModel.AccessTokenSecret)
    
    def __del__(self): 
        if self.session is not None:
            self.session.close()

    def ConvertPlacePreviewInputToPayload(self, previewOrderInput:PreviewOrderInput, isPlaceOrder = False):
        requestType = "PreviewOrderRequest"
        if isPlaceOrder is True:
            requestType = "PlaceOrderRequest"

        payload:dict = {}
        payload[requestType] = {}
        payload[requestType]["orderType"] = previewOrderInput.OrderType
        payload[requestType]["clientOrderId"] = previewOrderInput.ClientOrderId
        payload[requestType]["Order"] = []

        orderDetailList:List[OrderDetail] = previewOrderInput.Order
        orderdetail:dict = {}
        orderdetail["allOrNone"] = orderDetailList[0].AllOrNone
        orderdetail["priceType"] = orderDetailList[0].PriceType
        orderdetail["orderTerm"] = orderDetailList[0].OrderTerm
        orderdetail["marketSession"] = orderDetailList[0].MarketSession
        orderdetail["stopPrice"] = orderDetailList[0].StopPrice
        orderdetail["limitPrice"] = orderDetailList[0].LimitPrice
        orderdetail["Instrument"] = []

        instruments:List[Instrument] = orderDetailList[0].Instruments
        instrument:dict = {} 
        instrument["Product"] = {}
        instrument["Product"]["securityType"] = instruments[0].SecurityType
        instrument["Product"]["symbol"] = instruments[0].Symbol
        instrument["orderAction"] = instruments[0].OrderAction
        instrument["quantityType"] = instruments[0].QuantityType
        instrument["quantity"] = instruments[0].Quantity

        orderdetail["Instrument"].append(instrument)
        payload[requestType]["Order"].append(orderdetail)

        """
            {  
                "PreviewOrderRequest":
                {  
                    "orderType":"EQ",
                    "clientOrderId": "123ABC00000002",
                    "Order":
                    [  
                        {  
                            "allOrNone":"false",
                            "priceType":"LIMIT",
                            "orderTerm":"GOOD_FOR_DAY",
                            "marketSession":"REGULAR",
                            "stopPrice":"",
                            "limitPrice":"290",
                            "Instrument":[  
                            {  
                                "Product":{  
                                    "securityType":"EQ",
                                    "symbol":"FB"
                                },
                                "orderAction":"BUY",
                                "quantityType":"QUANTITY",
                                "quantity":"1"
                            }
                            ]
                        }
                    ]
                }
            }
        """

        return payload

    def CancelOrder(self, accountIdKey:str, orderId:int, 
                        accessToken:str = None, accessTokenSecret:str = None):

        params:dict = {}
        params["CancelOrderRequest"] = {}
        params["CancelOrderRequest"]["orderId"] = orderId

        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret
        
        url = self.settings.BaseUrl + "/v1/accounts/" + accountIdKey + "/orders/cancel.json"
        
        # Add parameters and header information
        headers = {"Content-Type": "application/json", "consumerKey": self.settings.ConsumerKey}
        # json.dumps(payload)
        response = self.session.put(url, header_auth=True, headers=headers, data=json.dumps(params))

        cancelOrderResponse = CancelOrderResponse()

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))
            data = response.json()
            responseProcessed = False

            if data is not None and "CancelOrderResponse" in data:
                responseProcessed = True
                if 'orderId' in data["CancelOrderResponse"]:
                    cancelOrderResponse.OrderId = int(data["CancelOrderResponse"]['orderId'])

            if data is not None and 'CancelOrderResponse' in data and 'Messages' in data["CancelOrderResponse"] \
                    and 'Message' in data["CancelOrderResponse"]["Messages"] \
                    and data["CancelOrderResponse"]["Messages"]["Message"] is not None:
                for error_message in data["CancelOrderResponse"]["Messages"]["Message"]:
                    message = Message()
                    message.Description = error_message["description"]
                    message.Code = error_message["code"]
                    message.Type = self.ParseMessageType(error_message["type"])
                    cancelOrderResponse.Messages.append(message)
                    responseProcessed = True

            if responseProcessed is False:
                message = Message()
                message.Description = self.strings.FatalUnhandledData.format(data)
                message.Code = self.strings.FatalErrorCode
                message.Type = self.ParseMessageType(self.strings.FatalType)
                cancelOrderResponse.Messages.append(message)           
        else:
            # Handle errors
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
            if response is not None and "headers" in response and "Content-Type" in response.headers \
                and response.headers['Content-Type'] == 'application/json' \
                and "Error" in response.json() and "message" in response.json()["Error"] \
                and response.json()["Error"]["message"] is not None:
                errorCode = ""
                if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                    errorCode = response.json()["Error"]["code"]
                cancelOrderResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
            else:
                errorCode = ""
                cancelOrderResponse.Error = Error(response.status_code, errorCode, response.text)
                try:
                    error = json.loads(response.text)
                    if("Error" in error and "message" in error["Error"]):
                        cancelOrderResponse.Error.Message = error["Error"]["message"]
                    if("Error" in error and "code" in error["Error"]):
                        cancelOrderResponse.Error.Code = error["Error"]["code"]
                except:
                    pass

        return cancelOrderResponse

    def PlaceOrderEQ(self, accountIdKey:str, previewOrderInput:PreviewOrderInput, 
                        previewIds:List[PreviewId], accessToken:str = None, accessTokenSecret:str = None):
        payload = self.ConvertPlacePreviewInputToPayload(previewOrderInput, isPlaceOrder=True)
        payload["PlaceOrderRequest"]["PreviewIds"] = []

        for previewId in previewIds:
            previewIdDict:dict = {}
            previewIdDict["previewId"] = previewId.PreviewId
            payload["PlaceOrderRequest"]["PreviewIds"].append(previewIdDict)

        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret

        url = self.settings.BaseUrl + "/v1/accounts/" + accountIdKey + "/orders/place.json"
        
        # Add parameters and header information
        headers = {"Content-Type": "application/json", "consumerKey": self.settings.ConsumerKey}
        # json.dumps(payload)
        response = self.session.post(url, header_auth=True, headers=headers, data=json.dumps(payload))
        
        placeOrderResponse = PlaceOrderResponse()
        placeOrderResponse.PlaceOrderResponseData = PlaceOrderResponseData()
        placeOrderResponse.PlaceOrderResponseData.OrderIds = []
        placeOrderResponse.PlaceOrderResponseData.OrderDetails = []

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))
            data = response.json()
            responseProcessed = False

            if data is not None and "PlaceOrderResponse" in data:
                responseProcessed = True
                if 'OrderIds' in data["PlaceOrderResponse"]:
                    for orderId in data["PlaceOrderResponse"]["OrderIds"]:
                        orderIdData = OrderId()
                        if 'orderId' in orderId:
                            orderIdData.OrderId = int(orderId["orderId"])
                        if 'cashMargin' in orderId:
                            orderIdData.CashMargin = str(orderId["cashMargin"])
                        placeOrderResponse.PlaceOrderResponseData.OrderIds.append(orderIdData)
                if 'totalOrderValue' in data["PlaceOrderResponse"]:
                    placeOrderResponse.PlaceOrderResponseData.TotalOrderValue = float(data["PlaceOrderResponse"]['totalOrderValue'])
                if 'totalCommission' in data["PlaceOrderResponse"]:
                    placeOrderResponse.PlaceOrderResponseData.TotalCommission = float(data["PlaceOrderResponse"]['totalCommission'])
                if 'clientOrderId' in data["PlaceOrderResponse"]:
                    placeOrderResponse.PlaceOrderResponseData.ClientOrderId = str(data["PlaceOrderResponse"]['clientOrderId'])
                if 'orderId' in data["PlaceOrderResponse"]:
                    placeOrderResponse.PlaceOrderResponseData.OrderId = str(data["PlaceOrderResponse"]['orderId'])
                if 'Order' in data["PlaceOrderResponse"]:
                    for orderDetail in data["PlaceOrderResponse"]["Order"]:
                        orderDetailData = self.ParseOrderDetail(orderDetail)
                        placeOrderResponse.PlaceOrderResponseData.OrderDetails.append(orderDetailData)

            if data is not None and 'PlaceOrderResponse' in data and 'MessageList' in data["PlaceOrderResponse"] \
                    and 'Message' in data["PlaceOrderResponse"]["MessageList"] \
                    and data["PlaceOrderResponse"]["MessageList"]["Message"] is not None:
                for error_message in data["PlaceOrderResponse"]["MessageList"]["Message"]:
                    message = Message()
                    message.Description = error_message["description"]
                    message.Code = error_message["code"]
                    message.Type = self.ParseMessageType(error_message["type"])
                    placeOrderResponse.Messages.append(message)
                    responseProcessed = True

            if responseProcessed is False:
                message = Message()
                message.Description = self.strings.FatalUnhandledData.format(data)
                message.Code = self.strings.FatalErrorCode
                message.Type = self.ParseMessageType(self.strings.FatalType)
                placeOrderResponse.Messages.append(message)           
        else:
            # Handle errors
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
            if response is not None and "headers" in response and "Content-Type" in response.headers \
                and response.headers['Content-Type'] == 'application/json' \
                and "Error" in response.json() and "message" in response.json()["Error"] \
                and response.json()["Error"]["message"] is not None:
                errorCode = ""
                if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                    errorCode = response.json()["Error"]["code"]
                placeOrderResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
            else:
                errorCode = ""
                placeOrderResponse.Error = Error(response.status_code, errorCode, response.text)
                try:
                    error = json.loads(response.text)
                    if("Error" in error and "message" in error["Error"]):
                        placeOrderResponse.Error.Message = error["Error"]["message"]
                    if("Error" in error and "code" in error["Error"]):
                        placeOrderResponse.Error.Code = error["Error"]["code"]
                except:
                    pass

        return placeOrderResponse
        
    def PreviewOrderEQ(self, accountIdKey:str, previewOrderInput:PreviewOrderInput,
            accessToken:str = None, accessTokenSecret:str = None):
        
        payload = self.ConvertPlacePreviewInputToPayload(previewOrderInput)
        
        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret

        url = self.settings.BaseUrl + "/v1/accounts/" + accountIdKey + "/orders/preview.json"
        
        # Add parameters and header information
        headers = {"Content-Type": "application/json", "consumerKey": self.settings.ConsumerKey}
        # json.dumps(payload)
        response = self.session.post(url, header_auth=True, headers=headers, data=json.dumps(payload))

        previewOrderResponse = PreviewOrderResponse()
        previewOrderResponse.PreviewOrderResponseData = PreviewOrderResponseData()
        previewOrderResponse.PreviewOrderResponseData.PreviewIds = []
        previewOrderResponse.PreviewOrderResponseData.OrderDetails = []

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))
            data = response.json()
            responseProcessed = False

            if data is not None and "PreviewOrderResponse" in data:
                responseProcessed = True
                if 'PreviewIds' in data["PreviewOrderResponse"]:
                    for previwId in data["PreviewOrderResponse"]["PreviewIds"]:
                        previwIdData = PreviewId()
                        if 'previewId' in previwId:
                            previwIdData.PreviewId = int(previwId["previewId"])
                        if 'cashMargin' in previwId:
                            previwIdData.CashMargin = str(previwId["cashMargin"])
                        previewOrderResponse.PreviewOrderResponseData.PreviewIds.append(previwIdData)
                if 'totalOrderValue' in data["PreviewOrderResponse"]:
                    previewOrderResponse.PreviewOrderResponseData.TotalOrderValue = float(data["PreviewOrderResponse"]['totalOrderValue'])
                if 'totalCommission' in data["PreviewOrderResponse"]:
                    previewOrderResponse.PreviewOrderResponseData.TotalCommission = float(data["PreviewOrderResponse"]['totalCommission'])
                if 'clientOrderId' in data["PreviewOrderResponse"]:
                    previewOrderResponse.PreviewOrderResponseData.ClientOrderId = str(data["PreviewOrderResponse"]['clientOrderId'])
                if 'Order' in data["PreviewOrderResponse"]:
                    for orderDetail in data["PreviewOrderResponse"]["Order"]:
                        orderDetailData = self.ParseOrderDetail(orderDetail)
                        previewOrderResponse.PreviewOrderResponseData.OrderDetails.append(orderDetailData)

            if data is not None and 'PreviewOrderResponse' in data and 'MessageList' in data["PreviewOrderResponse"] \
                    and 'message' in data["PreviewOrderResponse"]["MessageList"] \
                    and data["PreviewOrderResponse"]["MessageList"]["Message"] is not None:
                for error_message in data["PreviewOrderResponse"]["MessageList"]["Message"]:
                    message = Message()
                    message.Description = error_message["description"]
                    message.Code = error_message["code"]
                    message.Type = self.ParseMessageType(error_message["type"])
                    previewOrderResponse.Messages.append(message)
                    responseProcessed = True

            if responseProcessed is False:
                message = Message()
                message.Description = self.strings.FatalUnhandledData.format(data)
                message.Code = self.strings.FatalErrorCode
                message.Type = self.ParseMessageType(self.strings.FatalType)
                previewOrderResponse.Messages.append(message)           
        else:
            # Handle errors
            self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
            if response is not None and "headers" in response and "Content-Type" in response.headers \
                and response.headers['Content-Type'] == 'application/json' \
                and "Error" in response.json() and "message" in response.json()["Error"] \
                and response.json()["Error"]["message"] is not None:
                errorCode = ""
                if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                    errorCode = response.json()["Error"]["code"]
                previewOrderResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
            else:
                errorCode = ""
                previewOrderResponse.Error = Error(response.status_code, errorCode, response.text)
                try:
                    error = json.loads(response.text)
                    if("Error" in error and "message" in error["Error"]):
                        previewOrderResponse.Error.Message = error["Error"]["message"]
                    if("Error" in error and "code" in error["Error"]):
                        previewOrderResponse.Error.Code = error["Error"]["code"]
                except:
                    pass

        return previewOrderResponse

    def Orders(self, accountIdKey:str, accessToken:str = None, accessTokenSecret:str = None,
                filteringAndPagingParams:OrdersFilteringAndPagingParams = None
            ):

        pageSize = 50
        params = {}
        accumulateAndReturnAll:bool = False

        if filteringAndPagingParams is not None and filteringAndPagingParams.PageSize > 0:
            pageSize = filteringAndPagingParams.PageSize
        if filteringAndPagingParams is not None and filteringAndPagingParams.Params is not None and len(filteringAndPagingParams.Params) != 0:
            params = filteringAndPagingParams.Params

        if filteringAndPagingParams is None:
            accumulateAndReturnAll = True
        elif filteringAndPagingParams is not None and filteringAndPagingParams.ApplyFilterAndReturnAll is True:
            accumulateAndReturnAll = True
                        
        if "count" not in params:      
            params["count"] = pageSize

        # URL for the API endpoint
        url = self.settings.BaseUrl + "/v1/accounts/" + accountIdKey + "/orders.json"

        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret

        ordersResponse = OrdersResponse()
        ordersResponse.Orders = []
        ordersResponse.Messages = []

        try:

            # Make API call for GET request
            while True:
                response = self.session.get(url, header_auth=True, 
                            params = params)
                self.context.AppLogger.Logger.debug(self.strings.RequestHeader.format(response.request.headers))

                # Handle and parse response
                if response is not None and response.status_code == 200:
                    parsed = json.loads(response.text)
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))
                    data = response.json()
                    responseProcessed = False

                    if data is not None and "OrdersResponse" in data:
                        ordersResponseData = data["OrdersResponse"]
                        params = {}
                        ordersResponse.Next = ""
                        ordersResponse.Marker = ""
                        if ordersResponseData is not None and "next" in ordersResponseData:
                            ordersResponse.Next = str(ordersResponseData["next"])
                            params = dict(parse.parse_qsl(parse.urlsplit(ordersResponse.Next).query))
                        if ordersResponseData is not None and "marker" in ordersResponseData:
                            ordersResponse.Marker = str(ordersResponseData["marker"])
                        if ordersResponseData is not None and "Order" in ordersResponseData:
                            if ordersResponse.Orders is None:
                                ordersResponse.Orders = []
                            for order in ordersResponseData["Order"]:
                                orderData = Order()
                                if order is not None and "orderId" in order:
                                    orderData.OrderId = int(order["orderId"])
                                if order is not None and "orderType" in order:
                                    orderData.OrderType = str(order["orderType"])
                                if order is not None and "totalOrderValue" in order:
                                    orderData.TotalOrderValue = float(order["totalOrderValue"])
                                if order is not None and "totalCommission" in order:
                                    orderData.TotalCommission = float(order["totalCommission"])
                                if order is not None and "OrderDetail" in order:
                                    orderData.OrderDetails = []
                                    for orderDetail in order["OrderDetail"]:
                                        orderDetailData = self.ParseOrderDetail(orderDetail)
                                        orderData.OrderDetails.append(orderDetailData)
                                if order is not None and "Events" in order and "Event" in order["events"]:
                                    orderData.Events = []
                                    for event in order["Events"]["Event"]:
                                        eventData = Event()
                                        if event is not None and "name" in event:
                                            eventData.Name = str(event["name"])
                                        if event is not None and "dateTime" in event:
                                            eventData.DateTime = int(event["dateTime"])
                                        if event is not None and "orderNumber" in event:
                                            eventData.OrderNumber = int(event["orderNumber"])
                                        if event is not None and "instrument" in event:
                                            eventData.Instruments = []
                                            for instrument in event["instrument"]:
                                                instrumentData = self.ParseInstrument(instrument)
                                                if instrumentData is not None:
                                                    orderDetailData.Instruments.append(instrumentData)
                                        orderData.Events.append(eventData)   

                                ordersResponse.Orders.append(orderData)
                                responseProcessed = True
                    else:
                        # Handle errors
                        responseProcessed = True
                        self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
                        if response is not None and "headers" in response and "Content-Type" in response.headers \
                                and response.headers['Content-Type'] == 'application/json' \
                                and "Error" in response.json() and "message" in response.json()["Error"] \
                                and response.json()["Error"]["message"] is not None:
                            errorCode = ""
                            if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                                errorCode = response.json()["Error"]["code"]
                            ordersResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                        else:
                            ordersResponse.Error = Error(response.status_code, errorCode, response.text)
                            errorCode = ""
                            try:
                                error = json.loads(response.text)
                                if("Error" in error and "message" in error["Error"]):
                                    ordersResponse.Error.Message = error["Error"]["message"]
                                if("Error" in error and "code" in error["Error"]):
                                    ordersResponse.Error.Code = error["Error"]["code"]
                            except:
                                pass

                    if data is not None and 'OrdersResponse' in data and 'Messages' in data["OrdersResponse"] \
                                and 'Message' in data["OrdersResponse"]["Messages"] \
                                and data["OrdersResponse"]["Messages"]["Message"] is not None:
                        for error_message in data["OrdersResponse"]["Messages"]["Message"]:
                            message = Message()
                            message.Description = error_message["description"]
                            message.Code = error_message["code"]
                            message.Type = self.ParseMessageType(error_message["type"])
                            ordersResponse.Messages.append(message)
                            responseProcessed = True

                    if responseProcessed is False:
                        message = Message()
                        message.Description = self.strings.FatalUnhandledData.format(data)
                        message.Code = self.strings.FatalErrorCode
                        message.Type = self.ParseMessageType(self.strings.FatalType)
                        ordersResponse.Messages.append(message)           
                                                
                elif response is not None and response.status_code == 204:
                    break
                else:
                    # Handle errors
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
                    if response is not None and "headers" in response and "Content-Type" in response.headers \
                            and response.headers['Content-Type'] == 'application/json' \
                            and "Error" in response.json() and "message" in response.json()["Error"] \
                            and response.json()["Error"]["message"] is not None:
                        errorCode = ""
                        if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                            errorCode = response.json()["Error"]["code"]
                        ordersResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                    else:
                        errorCode = ""
                        ordersResponse.Error = Error(response.status_code, errorCode, response.text)
                        try:
                            error = json.loads(response.text)
                            if("Error" in error and "message" in error["Error"]):
                                ordersResponse.Error.Message = error["Error"]["message"]
                            if("Error" in error and "code" in error["Error"]):
                                ordersResponse.Error.Code = error["Error"]["code"]
                        except:
                            pass
                
                if accumulateAndReturnAll is False:
                    break                
                if ordersResponse.Error is not None and ordersResponse.Error.ResponseStatusCode != "":
                    break
                elif ordersResponse.Marker == "":
                    break

        except:
            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.critical(self.strings.UnexpectedError.format(sys.exc_info()))
            raise

        return ordersResponse

    def ParseOrderDetail(self, orderDetail):
        orderDetailData = OrderDetail()
        if orderDetail is not None and "orderNumber" in orderDetail:
            orderDetailData.OrderNumber = int(orderDetail["orderNumber"])
        if orderDetail is not None and "placedTime" in orderDetail:
            orderDetailData.PlacedTime = int(orderDetail["placedTime"])
        if orderDetail is not None and "executedTime" in orderDetail:
            orderDetailData.ExecutedTime = int(orderDetail["executedTime"])
        if orderDetail is not None and "orderValue" in orderDetail:
            orderDetailData.OrderValue = float(orderDetail["orderValue"])
        if orderDetail is not None and "status" in orderDetail:
            orderDetailData.Status = str(orderDetail["status"])
        if orderDetail is not None and "orderTerm" in orderDetail:
            orderDetailData.OrderTerm = str(orderDetail["orderTerm"])
        if orderDetail is not None and "orderType" in orderDetail:
            orderDetailData.OrderType = str(orderDetail["orderType"])
        if orderDetail is not None and "priceType" in orderDetail:
            orderDetailData.PriceType = str(orderDetail["priceType"])
        if orderDetail is not None and "allOrNone" in orderDetail:
            orderDetailData.AllOrNone = bool(orderDetail["allOrNone"])
        if orderDetail is not None and "estimatedTotalAmount" in orderDetail:
            orderDetailData.EstimatedTotalAmount = float(orderDetail["estimatedTotalAmount"])
        if orderDetail is not None and "estimatedCommission" in orderDetail:
            orderDetailData.EstimatedCommission = float(orderDetail["estimatedCommission"])
        if orderDetail is not None and "estimatedFees" in orderDetail:
            orderDetailData.EstimatedFees = float(orderDetail["estimatedFees"])
        if orderDetail is not None and "limitPrice" in orderDetail:
            orderDetailData.LimitPrice = float(orderDetail["limitPrice"])
        if orderDetail is not None and "Instrument" in orderDetail:
            orderDetailData.Instruments = []
            for instrument in orderDetail["Instrument"]:
                instrumentData = self.ParseInstrument(instrument)
                if instrumentData is not None:
                    orderDetailData.Instruments.append(instrumentData)

        if orderDetail is not None and "messages" in orderDetail and "Message" in orderDetail["messages"]:
            orderDetailData.Messages = []
            for message in orderDetail["messages"]["Message"]:
                messageData = Message()
                if "description" in message:
                    messageData.Description = message["description"]
                if "code" in message:
                    messageData.Code = message["code"]
                if "type" in message:
                    messageData.Type = self.ParseMessageType(message["type"])
                orderDetailData.Messages.append(messageData)

        return orderDetailData

    def ParseInstrument(self, instrument):
        if instrument is None or "Product" not in instrument:
            return None

        instrumentData = Instrument()

        if "symbol" in instrument["Product"]:
            instrumentData.Symbol = str(instrument["Product"]["symbol"])
        if "securityType" in instrument["Product"]:
            instrumentData.SecurityType = str(instrument["Product"]["securityType"])
        if "orderAction" in instrument:
            instrumentData.OrderAction = str(instrument["orderAction"])
        if "averageExecutionPrice" in instrument:
            instrumentData.AverageExecutionPrice = float(instrument["averageExecutionPrice"])
        if "estimatedCommission" in instrument:
            instrumentData.EstimatedCommission = float(instrument["estimatedCommission"])
        if "estimatedFees" in instrument:
            instrumentData.EstimatedFees = float(instrument["estimatedFees"])
        if "cancelQuantity" in instrument:
            instrumentData.CancelQuantity = float(instrument["cancelQuantity"])
        if "orderedQuantity" in instrument:
            instrumentData.OrderedQuantity = float(instrument["orderedQuantity"])
        if "filledQuantity" in instrument:
            instrumentData.FilledQuantity = float(instrument["filledQuantity"])
        if "quantityType" in instrument:
            instrumentData.QuantityType = str(instrument["quantityType"])
        if "quantity" in instrument:
            instrumentData.Quantity = str(instrument["quantity"])
        
        return instrumentData
