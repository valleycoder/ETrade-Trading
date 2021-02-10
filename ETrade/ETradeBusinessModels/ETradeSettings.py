class ETradeSettings:

    """ ETrade Account related settings.

        Attributes:

        BaseUrl - static field. ETrade base url.

        ConsumerKey - static field. Account consumer key.

        ConsumerSecret - static field. Account consumer secret.

        AccountIdKey - static field. Unique key associated with the Account. This can be obtained by
        using the EntryAccount python script.

        RequestTokenUrl - static field. RequestTokenUrl.

        AccessTokenUrl - static field. AccessTokenUrl.

        AuthorizeUrl - static field. AuthorizeUrl.

        AccessTokenRenewUrl - static field.AccessTokenRenewUrl.

        AccountUserName - static field. User Name.

        AccountPassword - static field. Password.

        CommissionType - static field. CommissionType = 1, Commission is Fixed Value. CommissionType = 2, Commission is Percentage.

        BuyCommission - static field. Buy commission value or percentage. Commission should also include Extended trading hours costs if any.

        SellCommission - static field. Sell commission value or percentage. Commission should also include Extended trading hours costs if any.

        ExclusionErrorCodes - static field. These errors can be ignored and application can continue.
        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/ErrorCodes

        DangerErrorCodes - static field. System cannot continue when these errors occur.
        https://apisb.etrade.com/docs/api/order/api-order-v1.html#/definitions/ErrorCodes

    """

    BaseUrl = "https://api.etrade.com"

    ConsumerKey = "consumer key"
    ConsumerSecret = "consumer secret"
    AccountIdKey = "account id key"
    
    RequestTokenUrl = "https://api.etrade.com/oauth/request_token"
    AccessTokenUrl = "https://api.etrade.com/oauth/access_token"
    AuthorizeUrl = "https://us.etrade.com/e/t/etws/authorize?key={}&token={}"
    AccessTokenRenewUrl = "https://api.etrade.com/oauth/renew_access_token"

    AccountUserName = "username"
    AccountPassword = "password"

    # CommissionType = 1, Commission is Fixed Value. CommissionType = 2, Commission is Percentage.
    CommissionType = 1 
    BuyCommission = 0
    SellCommission = 0

    ExclusionErrorCodes = [8400, 1021, 163, 5003, 5011, 612]
    DangerErrorCodes = [9010]

    def __init__(self):
        pass
