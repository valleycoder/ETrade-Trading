from Entries.EntryInputs.EntryInput import EntryInput
from ETrade.ETradeBusinessServices.ETradeOrder import ETradeOrder


class EntryOrderInput(EntryInput):
    """ Input for EntryOrder driver program.
        Inherts from EntryInput.

        Attributes:

        Order:ETradeOrder - ETrade Order object.

    """
    def __init__(self):
        super().__init__()
        self.Order:ETradeOrder = ETradeOrder(inputModel = self.InputModel, settings = self.ETradeSettings, 
                                context = self.Context, strings = self.Strings)

