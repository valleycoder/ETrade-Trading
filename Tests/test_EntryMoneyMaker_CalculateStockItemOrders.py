import os
import sys
import unittest
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.OrderInfo import OrderInfo
from BusinessModels.PortfolioResponse import PortfolioPosition
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType
from BusinessModels.Settings import Settings
from Entries.EntryHelpers.ManageOrdersHelpers import ManageOrdersHelpers
from Entries.EntryInputs.EntryMoneyMakerInput import EntryMoneyMakerInput
from Entries.EntryMoneyMaker import MoneyMaker


class tests_ManageOrdersHelpers_GeneratePossibleLimitOrders(unittest.TestCase):
    """ Tests related to GeneratePossibleLimitOrders method of ManagerOrdersHelpers class.
    """

    def setUp(self):
        # Initialize the object.
        self.manageOrdersHelpers:ManageOrdersHelpers = ManageOrdersHelpers(Settings())
        entryInput = EntryMoneyMakerInput()
    
        self.moneyMaker = MoneyMaker(entryInput, self.manageOrdersHelpers)
        
    def tearDown(self):
        pass

    def test_CalculateStockItemOrders(self):
        """ CalculateStockItemOrders
            
            Symbol = "XXXX"

            FLAT Buy pricing.

            SellStepType = SellDeltaType.FIXED

            StartPrice = 20.55

            quantity = 2

            BuyStepSize = 1

            SellStepSize = 2

            QuantityMultiplier =  1

            MaxActiveBuy = 2

            Portfolio quantity = 9

            Expected Cancel Orders = 
                [
                    OrderInfo(Settings.NewOrderId, symbol, 22.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 21.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 20.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 19.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 18.55, 1, True, True),
                    OrderInfo(Settings.NewOrderId, symbol, 16.55, 1, True, False),
                    OrderInfo(Settings.NewOrderId, symbol, 15.55, 2, False, False)
                ]

            Expected Place Orders = 
                [

                ]
                

        """
        symbol = "XXXX"

        # Create ActiveStockItem
        activeStockItem = ActiveStockItem(symbol=symbol)
        quantity = 2
        buyStepSize = 1
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.StartPrice = 20.55
        activeStockItem.QuantityMultiplier = 1
        activeStockItem.MaxActiveBuy = 2
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        # Create PortfolioPosition
        portfolioPosition = PortfolioPosition(symbol=symbol)
        portfolioPosition.Quantity = 9
                        
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 22.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 21.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 20.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 19.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 18.55, 1, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 16.55, 1, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 15.55, 2, False, False)
        ]

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioPosition.Quantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)

        placeOrders, cancelOrders = self.moneyMaker.CalculateStockItemOrders(activeStockItem, [], portfolioPosition)

        print(placeOrders)

        print(cancelOrders)
    
    
if __name__ == '__main__':
    unittest.main()
