from Entries.EntryInputs.EntryInput import EntryInput
from ETrade.ETradeBusinessServices.ETradeMarket import ETradeMarket


class EntryMarketInput(EntryInput):
    """ Input for EntryMarket driver program.
        Inherts from EntryInput.

        Attributes:

        Market:ETradeMarket - ETrade market object.

    """
    def __init__(self):
        super().__init__()
        self.Market:ETradeMarket = ETradeMarket(inputModel = self.InputModel, settings = self.ETradeSettings, 
                                context = self.Context, strings = self.Strings)   

