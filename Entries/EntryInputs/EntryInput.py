from BusinessModels.Context import Context
from BusinessModels.Settings import Settings
from BusinessUtils.AppLogger import AppLogger
from Entries.EntryHelpers.LogHelper import LogMessage
from ETrade.ETradeBusinessModels.ETradeInputModel import ETradeInputModel
from ETrade.ETradeBusinessModels.ETradeSettings import ETradeSettings
from ETrade.ETradeBusinessServices.ETradeAuthorization import \
    ETradeAuthorization
from ETrade.ETradeBusinessUtils.ETradeConfiguration import ETradeConfiguration
from Strings.FormatStringsBase import FormatStringsBase


class EntryInput:
    """ Base class for the Entry Inputs. The Entry scripts are the driver programs which need lot
        of input values. Instead of importing and creating the variables within the scripts, the required 
        input variables are generated within the Entry Inputs.

        Not a good programming practice. But it's much convenient and easy to manage.

        Attributes:

        Settings:Settings - Standard settings in the system.

        ETradeSettings:ETradeSettings - ETrade settings.

        Configuration:ETradeConfiguration - ETrade configuration.

        Strings:FormatStringsBase - Some standard strings in the system.

        Logger:AppLogger - Logger wrapper.

        Context:Context - Context to store any standard objects.

        InputModel:ETradeInputModel - ETrade input.

        Auth:ETradeAuthorization - Authorization service object.

        LogMessage - Log message method. All the entry level logging goes through this method.
        Very useful for testing purposes.

    """
    def __init__(self):
        
        self.Settings:Settings = Settings()
        self.ETradeSettings:ETradeSettings = ETradeSettings()
        self.Configuration:ETradeConfiguration = ETradeConfiguration(self.Settings.ConfigFilePathWithName)

        self.Strings:FormatStringsBase = FormatStringsBase()
        self.Logger:AppLogger = AppLogger(self.Settings.LogFilePathWithName, "AppLogger")
        self.Context:Context = Context(logger = self.Logger)
        accessToken, accessTokenSecret, dateTimeObj = self.Configuration.GetLatestETradeAccessKeyDetails()
        self.InputModel:ETradeInputModel = ETradeInputModel(accessToken, accessTokenSecret, dateTimeObj) 
        self.Auth:ETradeAuthorization = ETradeAuthorization(self.InputModel, self.ETradeSettings, self.Context, self.Strings)
        self.LogMessage = LogMessage                
