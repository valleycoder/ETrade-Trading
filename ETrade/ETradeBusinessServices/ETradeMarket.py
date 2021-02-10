import json
import sys

from BusinessModels.Context import Context
from BusinessModels.Error import Error
from BusinessModels.Message import Message
from BusinessModels.QuoteResponse import QuoteData, QuoteResponse
from ETrade.ETradeBusinessModels.ETradeInputModel import ETradeInputModel
from ETrade.ETradeBusinessModels.ETradeSettings import ETradeSettings
from ETrade.ETradeBusinessServices.ETradeBusinessService import \
    ETradeBusinessService
from rauth import OAuth1Session
from Strings.FormatStringsBase import FormatStringsBase


class ETradeMarket(ETradeBusinessService):
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

    def Quotes(self, symbols: list, accessToken:str = None, accessTokenSecret: str = None):

        # URL for the API endpoint
        url = self.settings.BaseUrl + "/v1/market/quote/" + ','.join(symbols) + ".json"

        session = OAuth1Session(self.settings.ConsumerKey,
            self.settings.ConsumerSecret,
            access_token = self.inputModel.AccessToken if accessToken is None else accessToken,
            access_token_secret = self.inputModel.AccessTokenSecret if accessTokenSecret is None else accessTokenSecret)

        quoteResponse = QuoteResponse()
        quoteResponse.QuoteData = []
        quoteResponse.Messages = []

        try:

            # Make API call for GET request
            response = session.get(url)

            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.debug(self.strings.RequestHeader.format(response.request.headers))
            
            if response is not None and response.status_code == 200:

                parsed = json.loads(response.text)
                if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))

                # Handle and parse response
                data = response.json()
                responseProcessed = False
                if data is not None and "QuoteResponse" in data and "QuoteData" in data["QuoteResponse"]:
                    for quote in data["QuoteResponse"]["QuoteData"]:
                        quoteData = QuoteData()
                        if quote is not None and "dateTime" in quote:
                            quoteData.DateTime = quote["dateTime"]
                        if quote is not None and "Product" in quote and "symbol" in quote["Product"]:
                            quoteData.Symbol = quote["Product"]["symbol"]
                        if quote is not None and "Product" in quote and "securityType" in quote["Product"]:
                            quoteData.SecurityType = quote["Product"]["securityType"]
                        if quote is not None and "All" in quote and "lastTrade" in quote["All"]:
                            quoteData.LastTradedPrice = str(quote["All"]["lastTrade"])
                        if quote is not None and "All" in quote and "adjustedFlag" in quote["All"]:
                            quoteData.AdjustedFlag = bool(quote["All"]["adjustedFlag"])
                        quoteResponse.QuoteData.append(quoteData)
                        responseProcessed = True
                if data is not None and 'QuoteResponse' in data and 'Messages' in data["QuoteResponse"] \
                            and 'Message' in data["QuoteResponse"]["Messages"] \
                            and data["QuoteResponse"]["Messages"]["Message"] is not None:
                    for error_message in data["QuoteResponse"]["Messages"]["Message"]:
                        message = Message()
                        message.Description = error_message["description"]
                        message.Code = error_message["code"]
                        message.Type = self.ParseMessageType(error_message["type"])
                        quoteResponse.Messages.append(message)
                        responseProcessed = True

                if responseProcessed is False:
                    message = Message()
                    message.Description = self.strings.FatalUnhandledData.format(data)
                    message.Code = self.strings.FatalErrorCode
                    message.Type = self.ParseMessageType(self.strings.FatalType)
                    quoteResponse.Messages.append(message)

            else:

                if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response))
                    self.context.AppLogger.Logger.debug(self.strings.ResponseContent.format(response.content))
                    self.context.AppLogger.Logger.debug(self.strings.ResponseCode.format(response.status_code))
                errorCode = ""
                quoteResponse.Error = Error(response.status_code, errorCode, response.text)
                try:
                    error = json.loads(response.text)
                    if("Error" in error and "message" in error["Error"]):
                        quoteResponse.Error.Message = error["Error"]["message"]
                    if("Error" in error and "code" in error["Error"]):
                        quoteResponse.Error.Code = error["Error"]["code"]
                except:
                    pass
        
        except:
            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.critical(self.strings.UnexpectedError.format(sys.exc_info()))
            raise
        finally:
            if session is not None:
                session.close()

        return quoteResponse
