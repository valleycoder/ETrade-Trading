
class Settings:
    """ Some standard settings in the system.

        ConfigFilePathWithName - Configuration file path. Access token information is stored in
        the config file.

        ChromeDriverPathWithName - Path to the chrome driver package/exe.

        LogFilePathWithName - System wide log file path.

        MoneyMakerLogFilePathWithName - Money maker log file path.

        IsAuthorizationManual - If True, Authorization is done manually. This is useful if for some
        reason chromedriver is not working.

        CycleWaitTimeInSeconds - Wait time between main loop itterations in seconds.

        NewOrderId - Placeholder OrderId for orders which are about to be placed.

        FloatRoundPrecision - Floating point precision.

        MaxCommission - For small traders commission is very critical. If commission changes we should
        abort and find out what the commission is.

        UnfilledCommissionOrFee - Some commission and fee related fields are initialized with this 
        value and later verified if the fields are populated by the API or not.

        UnfilledValue - Some fields are initialized with this value and later verified if the fields 
        are populated by the API or not.

    """
    
    ConfigFilePathWithName = "C://Users//**//TradingTools//Python//Trading//Entries//config.ini"
    # ChromeDriverPathWithName = "//Users/**//Trading//Trading-1//ChromeDriver//Mac//V86//chromedriver"
    ChromeDriverPathWithName = "C://Users//**//Trading//ChromeDriver//Windows//V86//chromedriver.exe"
    LogFilePathWithName = "C://Users//**//TradingTools//Python//Trading//Entries//trader_client.log"
    MoneyMakerLogFilePathWithName = "C://Users//**//TradingTools//Python//Trading//Entries//money_maker.log"
    IsAuthorizationManual = False
    CycleWaitTimeInSeconds = 60
    NewOrderId = -9999
    FloatRoundPrecision = 2
    MaxCommission = 0.1
    UnfilledCommissionOrFee = -99999999999999
    UnfilledValue = -99999999999999
      
    def __init__(self):
        pass
