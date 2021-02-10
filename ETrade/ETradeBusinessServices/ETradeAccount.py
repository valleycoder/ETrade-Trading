import json
import sys
from urllib import parse

from BusinessModels.AccountListResponse import AccountData, AccountListResponse
from BusinessModels.Context import Context
from BusinessModels.Error import Error
from BusinessModels.FilteringAndPagingParams import \
    PortfolioFilteringAndPagingParams
from BusinessModels.PortfolioResponse import (AccountPortfolio, PagingInfo,
                                              PortfolioPosition,
                                              PortfolioResponse)
from ETrade.ETradeBusinessModels.ETradeInputModel import ETradeInputModel
from ETrade.ETradeBusinessModels.ETradeSettings import ETradeSettings
from ETrade.ETradeBusinessServices.ETradeBusinessService import \
    ETradeBusinessService
from Exceptions.InvalidFilteringAndPagingParamsException import \
    InvalidPortfolioFilteringAndPagingParamsError
from rauth import OAuth1Session
from Strings.FormatStringsBase import FormatStringsBase


class ETradeAccount(ETradeBusinessService):
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

    def AccountList(self, accessToken:str = None, accessTokenSecret: str = None):
        # URL for the API endpoint
        url = self.settings.BaseUrl + "/v1/accounts/list.json"

        # Make API call for GET request
        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret

        accountListResponse = AccountListResponse()
        accountListResponse.AccountData = []

        try:

            response = self.session.get(url, header_auth=True)

            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.debug(self.strings.RequestHeader.format(response.request.headers))

            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))

                data = response.json()
                if data is not None and "AccountListResponse" in data and "Accounts" in data["AccountListResponse"] \
                        and "Account" in data["AccountListResponse"]["Accounts"]:
                    accounts = data["AccountListResponse"]["Accounts"]["Account"]
                    for account in accounts:
                        accountData = AccountData()
                        if account is not None and "accountId" in account:
                            accountData.AccountId = account["accountId"]
                        if account is not None and "accountDesc" in account:
                            accountData.AccountDesc = account["accountDesc"]
                        if account is not None and "accountIdKey" in account:
                            accountData.AccountIdKey = account["accountIdKey"]
                        accountListResponse.AccountData.append(accountData)
                else:
                    # Handle errors
                    if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                        self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
                    if response is not None and response.headers['Content-Type'] == 'application/json' \
                            and "Error" in response.json() and "message" in response.json()["Error"] \
                            and response.json()["Error"]["message"] is not None:
                        errorCode = ""
                        if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                            errorCode = response.json()["Error"]["code"]
                        accountListResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                    else:
                        errorCode = ""
                        accountListResponse.Error = Error(response.status_code, errorCode, response.text)
                        try:
                            error = json.loads(response.text)
                            if("Error" in error and "message" in error["Error"]):
                                accountListResponse.Error.Message = error["Error"]["message"]
                            if("Error" in error and "code" in error["Error"]):
                                accountListResponse.Error.Code = error["Error"]["code"]
                        except:
                            pass
                        
            else:
                # Handle errors
                if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(response.text))
                if response is not None and response.headers['Content-Type'] == 'application/json' \
                        and "Error" in response.json() and "message" in response.json()["Error"] \
                        and response.json()["Error"]["message"] is not None:
                    errorCode = ""
                    if "code" in response.json()["Error"] and response.json()["Error"]["code"] is not None:
                        errorCode = response.json()["Error"]["code"]
                    accountListResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                else:
                    errorCode = ""
                    accountListResponse.Error = Error(response.status_code, errorCode, response.text)
                    try:
                        error = json.loads(response.text)
                        if("Error" in error and "message" in error["Error"]):
                            accountListResponse.Error.Message = error["Error"]["message"]
                        if("Error" in error and "code" in error["Error"]):
                            accountListResponse.Error.Code = error["Error"]["code"]
                    except:
                        pass
        except:
            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.critical(self.strings.UnexpectedError.format(sys.exc_info()))
            raise

        return accountListResponse

    def Portfolio(self, accountIdKey:str, accessToken:str = None, accessTokenSecret:str = None,
                filteringAndPagingParams:PortfolioFilteringAndPagingParams = None
            ):

        pageSize = 50
        pageNumber = 1
        params = {}
        accumulateAndReturnAll:bool = False

        if filteringAndPagingParams is not None and filteringAndPagingParams.PageSize <= 0 and filteringAndPagingParams.PageNumber > 0:
            raise InvalidPortfolioFilteringAndPagingParamsError(self.strings.FilteringAndPagingParamsError.format("PageSize", filteringAndPagingParams.PageSize), 
                                            filteringAndPagingParams)
        if filteringAndPagingParams is not None and filteringAndPagingParams.PageNumber <= 0 and filteringAndPagingParams.PageSize > 0:
            raise InvalidPortfolioFilteringAndPagingParamsError(self.strings.FilteringAndPagingParamsError.format("PageNumber", filteringAndPagingParams.PageNumber), 
                                            filteringAndPagingParams)

        if filteringAndPagingParams is not None and filteringAndPagingParams.PageSize > 0:
            pageSize = filteringAndPagingParams.PageSize
        if filteringAndPagingParams is not None and filteringAndPagingParams.PageNumber > 0:
            pageNumber = filteringAndPagingParams.PageNumber
        if filteringAndPagingParams is not None and filteringAndPagingParams.Params is not None and len(filteringAndPagingParams.Params) != 0:
            params = filteringAndPagingParams.Params

        if filteringAndPagingParams is None:
            accumulateAndReturnAll = True
        elif filteringAndPagingParams is not None and filteringAndPagingParams.ApplyFilterAndReturnAll is True:
            accumulateAndReturnAll = True
        
        if "count" not in params:      
            params["count"] = pageSize

        if "pageNumber" not in params:
            params["pageNumber"] = pageNumber

        # URL for the API endpoint
        url = self.settings.BaseUrl + "/v1/accounts/" + accountIdKey + "/portfolio.json"

        if accessToken is not None:
            self.session.access_token = accessToken
        if accessTokenSecret is not None:
            self.session.access_token_secret = accessTokenSecret

        portfolioResponse = PortfolioResponse()
        portfolioResponse.AccountPortfolios = []
        portfolioResponse.AccountPortfolios.append(AccountPortfolio())
        portfolioResponse.AccountPortfolios[0].PortfolioPositions = []

        try:

            # Make API call for GET request
            while True:
                response = self.session.get(url, header_auth=True, 
                            params = params)
                # response = self.session.get(url, header_auth=True)
                self.context.AppLogger.Logger.debug(self.strings.RequestHeader.format(response.request.headers))

                # Handle and parse response
                if response is not None and response.status_code == 200:
                    parsed = json.loads(response.text)
                    self.context.AppLogger.Logger.debug(self.strings.ResponseBody.format(json.dumps(parsed, indent=4, sort_keys=True)))
                    data = response.json()

                    if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:
                        for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                            accountPortfolio = portfolioResponse.AccountPortfolios[0]
                            accountPortfolio.PagingInfo = PagingInfo()
                            accountPortfolio.PagingInfo.PageSize = pageSize
                            accountPortfolio.PagingInfo.NextPageNumber = 0
                            if "accountId" in acctPortfolio:
                                accountPortfolio.AccountId = acctPortfolio["accountId"]
                            if "totalNoOfPages" in acctPortfolio:
                                accountPortfolio.PagingInfo.TotalNumberOfPages = acctPortfolio["totalNoOfPages"]
                            if "nextPageNo" in acctPortfolio:
                                accountPortfolio.PagingInfo.NextPageNumber = acctPortfolio["nextPageNo"]
                            if "next" in acctPortfolio:
                                accountPortfolio.PagingInfo.Next = str(acctPortfolio["next"])
                                    
                            if acctPortfolio is not None and "Position" in acctPortfolio:                        
                                # accountPortfolio.PortfolioPositions = []
                                for position in acctPortfolio["Position"]:
                                    portfolioPosition = PortfolioPosition()
                                    if position is not None and "symbolDescription" in position:
                                        portfolioPosition.Symbol = str(position["symbolDescription"])
                                    if position is not None and "quantity" in position:
                                        portfolioPosition.Quantity = int(position["quantity"])
                                    if position is not None and "Quick" in position and "lastTrade" in position["Quick"]:
                                        portfolioPosition.LastPrice = float(position["Quick"]["lastTrade"])
                                    if position is not None and "pricePaid" in position:
                                        portfolioPosition.PricePaid = float(position["pricePaid"])
                                    if position is not None and "totalGain" in position:
                                        portfolioPosition.TotalGain = float(position["totalGain"])
                                    if position is not None and "marketValue" in position:
                                        portfolioPosition.MarketValue = float(position["marketValue"])
                                    # accountPortfolio.PortfolioPositions.append(portfolioPosition)
                                    portfolioResponse.AccountPortfolios[0].PortfolioPositions.append(portfolioPosition)
                            # portfolioResponse.AccountPortfolios.append(accountPortfolio)
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
                            portfolioResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                        else:
                            errorCode = ""
                            portfolioResponse.Error = Error(response.status_code, errorCode, response.text)
                            try:
                                error = json.loads(response.text)
                                if("Error" in error and "message" in error["Error"]):
                                    portfolioResponse.Error.Message = error["Error"]["message"]
                                if("Error" in error and "code" in error["Error"]):
                                    portfolioResponse.Error.Code = error["Error"]["code"]
                            except:
                                pass
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
                        portfolioResponse.Error = Error(response.status_code, errorCode, response.json()["Error"]["message"])
                    else:
                        errorCode = ""
                        portfolioResponse.Error = Error(response.status_code, errorCode, response.text)
                        try:
                            error = json.loads(response.text)
                            if("Error" in error and "message" in error["Error"]):
                                portfolioResponse.Error.Message = error["Error"]["message"]
                            if("Error" in error and "code" in error["Error"]):
                                portfolioResponse.Error.Code = error["Error"]["code"]
                        except:
                            pass

                if accumulateAndReturnAll is False:
                    break                
                if portfolioResponse.Error is not None and portfolioResponse.Error.ResponseStatusCode != "":
                    break
                elif portfolioResponse.AccountPortfolios[len(portfolioResponse.AccountPortfolios) - 1].PagingInfo.NextPageNumber == 0:
                    break
                else:
                    params = dict(parse.parse_qsl(parse.urlsplit(portfolioResponse.AccountPortfolios[len(portfolioResponse.AccountPortfolios) - 1].PagingInfo.Next).query))
                    pageNumber = portfolioResponse.AccountPortfolios[len(portfolioResponse.AccountPortfolios) - 1].PagingInfo.NextPageNumber

        except:
            if self.context.AppLogger is not None and self.context.AppLogger.Logger is not None:
                self.context.AppLogger.Logger.critical(self.strings.UnexpectedError.format(sys.exc_info()))
            raise

        return portfolioResponse
