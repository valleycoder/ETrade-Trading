from BusinessModels.FilteringAndPagingParams import (
    OrdersFilteringAndPagingParams, PortfolioFilteringAndPagingParams)

from Exceptions.ErrorException import Error


class InvalidOrdersFilteringAndPagingParamsError(Error):
    """ Exception used to represent when Filtering and Paging parameters for
        retrieving Orders is invalid.

        Attributes:

        FilteringAndPagingParams:OrdersFilteringAndPagingParams - params passed to the bussiness objects method.

        Message:str - text message.

    """
    def __init__(self, message:str, filteringAndPagingParams:OrdersFilteringAndPagingParams):
        self.FilteringAndPagingParams = filteringAndPagingParams
        self.Message = message


class InvalidPortfolioFilteringAndPagingParamsError(Error):
    """ Exception used to represent when Filtering and Paging parameters for
        retrieving Portfolio is invalid.

        Attributes:

        FilteringAndPagingParams:PortfolioFilteringAndPagingParams - params passed to the bussiness objects method..

        Message:str - text message.

    """
    def __init__(self, message:str, filteringAndPagingParams:PortfolioFilteringAndPagingParams):
        self.FilteringAndPagingParams = filteringAndPagingParams
        self.Message = message
