from typing import List

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType

from Entries.ActiveItem import ActiveItem
from Entries.PriceCoordinates import PriceCoordinates0


def GetActiveStockItem(activeItem:ActiveItem) -> ActiveStockItem:
    """ Helper function to convert the ActiveItem to ActiveStockItem.
        ActiveItem is received from the UI Module. ActiveItem to converted to the
        ActiveStockItem in this function.

        Parameters:

        activeItem:ActiveItem - ActiveItem object.

        Returns:

        ActiveStockItem object.


    """
    activeStockItem = ActiveStockItem(activeItem.Symbol)
    activeStockItem.StartPrice = activeItem.StartPrice
    activeStockItem.SellStepType = activeItem.SellStepType
    activeStockItem.SellStepSize = activeItem.SellStepSize
    activeStockItem.MaxActiveBuy = activeItem.MaxActiveBuy
    activeStockItem.QuantityMultiplier = activeItem.QuantityMultiplier

    # Price coordinate is selected based on the Quantity.
    # If Quantity > 0, then Quantity is used.
    # If Quantity == 0 then PriceCoordinates0 is used.
    # If Quantity == -1 then PriceCoordinates1 is used.
    # If Quantity == -2 then PriceCoordinates2 is used and so on.
    
    priceCoordinates:List[PriceCoordinate] = []
    if(activeItem.Quantity == 0):
        priceCoordinates = PriceCoordinates0
    elif(activeItem.Quantity > 0):
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=activeItem.Quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=activeItem.BuyStepSize))
    else:
        raise Exception("Fatal - Unsupported Quantity.")
    activeStockItem.PriceCoordinates = priceCoordinates
    return activeStockItem


# List of the stocks that are active in the system.
ActiveStockItems:List[ActiveStockItem] = []

# New stock item template.
# ActiveItem(symbol="XXX", startPrice="10", buyStepSize=0.25, sellStepSize=0.5, 
#   sellStepType = SellDeltaType.FIXED, quantity=10, maxActiveBuy=1, quantityMultiplier=1 )


ActiveStockItems.append(GetActiveStockItem(ActiveItem("XXXXX", 162.55, 2, 2, SellDeltaType.FIXED, 1, 0, 1)))
ActiveStockItems.append(GetActiveStockItem(ActiveItem("YXYXXX", 112.55, 2, 2, SellDeltaType.FIXED, 1, 0, 1)))
ActiveStockItems.append(GetActiveStockItem(ActiveItem("ABDD56", 17.05, 0.25, 0.25, SellDeltaType.FIXED, 1, 0, 1)))
ActiveStockItems.append(GetActiveStockItem(ActiveItem("XwdE", 24.55, 0.25, 0.25, SellDeltaType.FIXED, 1, 0, 1)))
ActiveStockItems.append(GetActiveStockItem(ActiveItem("LXzzE", 42.05, 0.5, 0.5, SellDeltaType.FIXED, 1, 0, 1)))

# Make sure all the stock symbols are in capital letters without any leading and trailing whitespaces.
for activeStockItem in ActiveStockItems:
    activeStockItem.Symbol = activeStockItem.Symbol.upper().strip()

# Check if there are any duplicates in the ActiveStockItems list.
if(len(ActiveStockItems) != len(set(activeStockItem.Symbol for activeStockItem in ActiveStockItems))):
    raise Exception("Fatal - Duplicate Symbols in Active Stock Items are not allowed.")

