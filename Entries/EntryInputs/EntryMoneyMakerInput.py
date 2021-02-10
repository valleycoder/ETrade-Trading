from typing import List

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessUtils.AppLogger import AppLogger
from Entries.ActiveStocks import ActiveStockItems
from Entries.EntryInputs.EntryInput import EntryInput
from ETrade.ETradeBusinessServices.ETradeAccount import ETradeAccount
from ETrade.ETradeBusinessServices.ETradeOrder import ETradeOrder


class EntryMoneyMakerInput(EntryInput):
    """ Input for EntryMoneyMaker driver program.
        Inherts from EntryInput.

        Attributes:

        ActiveStockItems:List[ActiveStockItem] - Active stock items in the system.

        MoneyMakerLogger:AppLogger - Separate logger for the MoneyMaker.
        
        Order:ETradeOrder - ETrade Order object.

        Account:ETradeAccount - ETrage Account object.

    """
    def __init__(self):
        super().__init__()

        self.ActiveStockItems:List[ActiveStockItem] = ActiveStockItems
        self.MoneyMakerLogger:AppLogger = AppLogger(self.Settings.MoneyMakerLogFilePathWithName, "MoneyMakerLogger")
        self.Order:ETradeOrder = ETradeOrder(inputModel = self.InputModel, settings = self.ETradeSettings, 
                                context = self.Context, strings = self.Strings)
        self.Account:ETradeAccount = ETradeAccount(inputModel = self.InputModel, settings = self.ETradeSettings, 
                                        context = self.Context, strings = self.Strings) 

