from datetime import datetime


class ETradeInputModel:
    """ Some non-constant input to the ETrade business services.

        AccessToken:str - ETrade Access token.

        AccessTokenSecret:str - ETrade Access token string.     

        AccessTokenDateTime:datetime - Latest time when this access token is used.

    """
    def __init__(self, accessToken: str, 
                    accessTokenSecret: str,
                    accessTokenDateTime: datetime):
        self.AccessToken = accessToken
        self.AccessTokenSecret = accessTokenSecret
        self.AccessTokenDateTime = accessTokenDateTime
    
