import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType

from Entries.EntryHelpers.ManageOrdersHelpers import ManageOrdersHelpers
from Entries.PriceCoordinates import PriceCoordinates0


def MaxInvestmentTest(manageOrdersHelpers:ManageOrdersHelpers, activeStockItems:List[ActiveStockItem]):
    """ function to calculate and display the maximum investment of the given stock items.

        Parameters:

        manageOrdersHelpers:ManageOrdersHelpers - Manage order helpers object containing the helper 
        methods to calculate the maximum investment.

        activeStockItems:List[ActiveStockItem] - List of active stock items.

    """

    # For each stock item, calculate and print the maximum investment.
    for activeStockItem in activeStockItems:
        maxInvestment:Decimal = manageOrdersHelpers.CalculateMaxInvestment(activeStockItem.StartPrice, activeStockItem.PriceCoordinates, activeStockItem.QuantityMultiplier)
        print(f"Symbol  -> {activeStockItem.Symbol}, Max Investment ->{maxInvestment}")


def GeneratePossibleLimitOrdersTest(manageOrdersHelpers:ManageOrdersHelpers):
    """ Generates and prints the possible limit orders. ActiveStockItem and portfolio quantity
        are hardcoded within the function.

        Parameters:

        manageOrdersHelpers:ManageOrdersHelpers - Manage order helpers object containing the helper 
        methods to calculate the maximum investment.

        Exceptions:

        Exception.

    """

    # Create active stock item.
    activeStockItem = ActiveStockItem(symbol="AAPL", startPrice=16, priceCoordinates=None,
    sellStepType= SellDeltaType.PERCENTAGE, sellStepSize=10, 
    maxActiveBuy=2, quantityMultiplier=1)

    # select a price coordinate.
    priceCoordinates:List[PriceCoordinate] = []
    x:int = 0
    if(x == 0):
        priceCoordinates = PriceCoordinates0
    elif(x > 0):
        quantity = 1
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=activeStockItem.BuyStepSize))

    # Portfolio quantity.
    portfolioPositionQuantity:int = 100

    # Set the price coordinates.
    activeStockItem.PriceCoordinates = priceCoordinates
    limitOrders = manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioPositionQuantity)

    # Make sure that the resulting sell quantity is same as the portfolio quanitity.
    count = 0
    for limitOrder in limitOrders:
        if(limitOrder.IsSell is True):
            count = count + limitOrder.Quantity

    if(count != portfolioPositionQuantity):
        raise Exception("Sell orders quantity did not match with the portfolio position quantity.")

    print(limitOrders)
    print(count)


if __name__ == "__main__":
    from BusinessModels.Settings import Settings

    from ActiveStocks import ActiveStockItems

    manageOrdersHelpers:ManageOrdersHelpers = ManageOrdersHelpers(Settings())
    MaxInvestmentTest(manageOrdersHelpers, ActiveStockItems)
    GeneratePossibleLimitOrdersTest(manageOrdersHelpers)
