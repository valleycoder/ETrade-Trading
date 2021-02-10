from typing import List

from BusinessModels.Error import Error


class AccountData:
    """ Data related to Account is managed in this class objects. 
        Mapping some of the information from the related ETrade API - https://apisb.etrade.com/docs/api/account/api-account-v1.html#/definitions/Account

        Attributes:

        AccountId - The user's account ID.	

        AccountIdKey - The unique account key.

        AccountDesc - Description of account.	

    """
    def __init__(self, accountId:str = "", accountIdKey:str = "", 
                    accountDesc:str = ""):
        self.AccountId = accountId
        self.AccountIdKey = accountIdKey
        self.AccountDesc = accountDesc


class AccountListResponse:
    """ Represents the list of accounts returned by the API.

        Mapping some of the information from the related ETrade API - https://apisb.etrade.com/docs/api/account/api-account-v1.html#/definitions/Account

        Attributes:

        AccountData - List of AccountData objects.

        Error - API response error(if any).

    """
    def __init__(self, error: Error = None, accountData: List[AccountData] = []):
        self.AccountData: List[AccountData] = accountData
        self.Error: Error = error
    