from typing import List

from BusinessModels.Error import Error
from BusinessModels.Settings import Settings


class PortfolioPosition:
    """ Portfolio item information is stored in this class objects.

        Attributes:

        Symbol - EQ Symbol.

        Quantity - Number of stocks. Initialized with predefined constant so that it is easy to verify whether 
        this field is filled by the API or not.

        LastPrice - Last price.

        PricePaid - Price paid. We don't use this information in our system.

        TotalGain - Total gain. This information is not useful for our algorithm.

        MarketValue - Current value of this stock items.

    """
    def __init__(self, symbol:str = ""):
        self.Symbol = symbol
        self.Quantity = Settings.UnfilledValue
        self.LastPrice:float = 0
        self.PricePaid:float = 0
        self.TotalGain:float = 0
        self.MarketValue:float = 0


class PagingInfo:
    """ Track the paging information. We need paging because API will have some maximum results 
        per request.

        Attributes:

        PageSize - Page size.

        NextPageNumber - Next page number.

        TotalNumberOfPages - Total number of pages.

        Next - Url of the next page.

    """
    def __init__(self, pageSize:int = 0, nextPageNumber:int = 0, 
                    totalNumberOfPages:int = 0, next:str = ""):
        self.PageSize = pageSize
        self.NextPageNumber = nextPageNumber
        self.TotalNumberOfPages = totalNumberOfPages
        self.Next = next


class AccountPortfolio:
    """ Lists the portfolio items for the given account Id.

        Attributes:

        AccountId - Account Id.

        PortfolioPositions - List of portfolio items.

        PagingInfo - Paging information to get to the next page.

    """
    def __init__(self, accountId:str = "", 
                    pagingInfo: PagingInfo = None,
                    portfolioPositions: List[PortfolioPosition] = []
                    ):
        self.AccountId = accountId
        self.PortfolioPositions: List[PortfolioPosition] = portfolioPositions
        self.PagingInfo: PagingInfo = pagingInfo


class PortfolioResponse:
    """ Portfolio response.

        Attributes:

        AccountPortfolios - List of account portfolios.

        Error - Error if any.

    """
    def __init__(self, error: Error = None,
                    accountPortfolios: List[AccountPortfolio] = []
                    ):        
        self.AccountPortfolios = accountPortfolios
        self.Error: Error = error
