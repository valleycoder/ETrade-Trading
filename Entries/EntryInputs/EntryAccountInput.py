from Entries.EntryInputs.EntryInput import EntryInput
from ETrade.ETradeBusinessServices.ETradeAccount import ETradeAccount


class EntryAccountInput(EntryInput):
    """ Input for EntryAccount driver program.
        Inherts from EntryInput.

        Attributes:

        Account:ETradeAccount - ETrade account object.

    """
    def __init__(self):
        super().__init__()
        self.Account:ETradeAccount = ETradeAccount(inputModel = self.InputModel, settings = self.ETradeSettings, 
                                        context = self.Context, strings = self.Strings) 

