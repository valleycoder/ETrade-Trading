import configparser
import time
from datetime import datetime
from typing import Tuple


class ETradeConfiguration:
    """ ETrade access key can be reused for 24 hours so this information is persisted in .INI config file.

        Attributes:

        ETradeKeySectionString - Static field. INI config section name of the Access Keys information.

        ETradeAccessTokenString - Static field. Access Token field name in the config section.

        ETradeAccessTokenSecretString - Static field. Token secret field name in the config section.

        ETradeAccessTokenDateString - Static field. Date string field name in the config section.

        DateTimeFormat - Static field. Format in which datetime object is stored. Useful for serializing/deserializing.

        Methods:

        GetLatestETradeAccessKeyDetails() ->  Tuple[str, str, datetime] 
            Gets the access keys information stored in the config file. Returns tuple [AccessKey, AccessToken, LastAccessTimeStamp]

        StoreETradeAccessKeys(accessToken, accessTokenSecret, dateTimeObj) -> None
            Stores the access keys information to the config file.

    """
    ETradeKeySectionString = 'ETradeAccessKeys'
    ETradeAccessTokenString = 'AccessToken'
    ETradeAccessTokenSecretString = 'AccessTokenSecret'
    ETradeAccessTokenDateString = 'AccessTimeStamp'
    DateTimeFormat = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, configPath:str):
        """ Initialization method.

            Parameters:

            configPath - Path to the config file with name.

        """
        self.configPath = configPath
        self.config = configparser.ConfigParser()
        self.config.read(configPath)
        # config.read('Trading\\config.ini')
        # config.read('\\ETradeTools\\Python\\Trading\\config.ini')

    def GetLatestETradeAccessKeyDetails(self) -> Tuple[str, str, datetime]:
        """Gets the access keys information stored in the config file. 
            Returns tuple [AccessKey, AccessToken, LastAccessTimeStamp]
        """
        accessToken = self.config[self.ETradeKeySectionString][self.ETradeAccessTokenString]
        accessTokenSecret = self.config[self.ETradeKeySectionString][self.ETradeAccessTokenSecretString]
        dateTimeObj = datetime.strptime(self.config[self.ETradeKeySectionString][self.ETradeAccessTokenDateString], self.DateTimeFormat)
        return (accessToken, accessTokenSecret, dateTimeObj)
        
    def StoreETradeAccessKeys(self, accessToken:str, accessTokenSecret:str, dateTimeObj:datetime) -> None:
        """Stores the access keys information to the config file.

            Parameters:

            accessToken - Access token.

            accessTokenSecret - Access token secret.

            dateTimeObj:datetime - Date and time when the access key was last used.

        """
        dateTimeStr = dateTimeObj.now().strftime(self.DateTimeFormat)
        self.config.set(self.ETradeKeySectionString, self.ETradeAccessTokenString, accessToken)
        self.config.set(self.ETradeKeySectionString, self.ETradeAccessTokenSecretString, accessTokenSecret)
        self.config.set(self.ETradeKeySectionString, self.ETradeAccessTokenDateString, dateTimeStr)

        # Store to the config file.
        with open(self.configPath, 'w') as f:
            self.config.write(f)

        # Sleep is needed to avoid retrieving stale data.
        # Not harmful. Need to figure out why this is needed.
        time.sleep(.1)
            
