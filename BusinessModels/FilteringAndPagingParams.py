from enum import Enum, unique


@unique
class SortOrder(Enum):
    """ Sort order ASC or DESC

    """
    ASC = 1
    DESC = 2


@unique
class PortfolioSortBy(Enum):
    """ Sort by SYMBOL or QUANTITY for portfolio API call.

    """
    SYMBOL = 1
    QUANTITY = 2


class PortfolioFilteringAndPagingParams:
    """ Represents paging and filtering information passed to the Portfolio API.
        This class representation is incomplete because we are not using Sorting in the 
        application.

        Attributes:

        ApplyFilterAndReturnAll -  Applies the filter and returns all the records. API may not be able 
        to return all the records in a single call because of maximum page size limit. ApplyFilterAndReturnAll
        instructs the related methods to call the API repeatedly till we get all the records matching the criteria.

        PageSize - Page size.

        PageNumber - Page number.

        Next - While paging you need the Url of the next page. Next contains the next page Url. You still need to apply
        the same filter for the API call.

        Params - Dictionary of the filter parameters. Url - https://apisb.etrade.com/docs/api/account/api-portfolio-v1.html 
        contains params list.

    """

    def __init__(self, applyFilterAndReturnAll:bool = False, pageSize:int = 0, pageNumber:int = 0):
        self.ApplyFilterAndReturnAll:bool = applyFilterAndReturnAll
        self.PageSize = pageSize
        self.PageNumber = pageNumber
        self.Next = ""
        self.Params:dict = {}


class OrdersFilteringAndPagingParams:
    """ Represents paging and filtering information passed to the Orders API.
        This class representation is incomplete because we are not using all the features in the
        application.

        Attributes:

        ApplyFilterAndReturnAll -  Applies the filter and returns all the records. API may not be able 
        to return all the records in a single call because of maximum page size limit. ApplyFilterAndReturnAll
        instructs the related methods to call the API repeatedly till we get all the records matching the criteria.

        PageSize - Page size.


        Next - While paging you need the marker Url of the next page. Next contains the next page Url with marker. You still need to apply
        the same filter for the API call.

        Params - Dictionary of the filter parameters. Url - https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definition/getOrders
        contains params list.

    """
    def __init__(self, applyFilterAndReturnAll:bool = False, pageSize:int = 0):
        self.ApplyFilterAndReturnAll:bool = applyFilterAndReturnAll
        self.PageSize:int = pageSize
        self.Next:str = ""
        self.Params:dict = {}
