import os
import sys
import unittest
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.OrderInfo import OrderInfo
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType
from BusinessModels.Settings import Settings
from Entries.EntryHelpers.ManageOrdersHelpers import ManageOrdersHelpers
from Entries.PriceCoordinates import PriceCoordinates0

from Tests.test_Data import PriceCoordinates1001


class tests_ManageOrdersHelpers_GeneratePossibleLimitOrders(unittest.TestCase):
    """ Tests related to GeneratePossibleLimitOrders method of ManagerOrdersHelpers class.
    """

    def setUp(self):
        # Initialize the object.
        self.manageOrdersHelpers = ManageOrdersHelpers(Settings())

    def tearDown(self):
        pass

    def test_GeneratePossibleLimitOrders_BuyType_FLAT_SellType_FIXED(self):
        """ GeneratePossibleLimitOrders
            
            FLAT Buy pricing.

            SellStepType = SellDeltaType.FIXED

            StartPrice = 20.55

            quantity = 2

            BuyStepSize = 1

            SellStepSize = 2

            QuantityMultiplier =  1

            MaxActiveBuy = 2

            Portfolio quantity = 9

            Expected Orders = 
                [
                    OrderInfo(Settings.NewOrderId, symbol, 22.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 21.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 20.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 19.55, 2, False, True),
                    OrderInfo(Settings.NewOrderId, symbol, 18.55, 1, True, True),
                    OrderInfo(Settings.NewOrderId, symbol, 16.55, 1, True, False),
                    OrderInfo(Settings.NewOrderId, symbol, 15.55, 2, False, False)
                ]
                

        """
        symbol = "XXXX"
        activeStockItem = ActiveStockItem(symbol=symbol)
        quantity = 2
        buyStepSize = 1
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.StartPrice = 20.55
        activeStockItem.QuantityMultiplier = 1
        activeStockItem.MaxActiveBuy = 2

        portfolioQuantity = 9
                
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 22.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 21.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 20.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 19.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 18.55, 1, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 16.55, 1, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 15.55, 2, False, False)
        ]

        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioQuantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)

    def test_GeneratePossibleLimitOrders_BuyType_PROGRESSIVE_SellType_FIXED(self):
        """ GeneratePossibleLimitOrders
            
            PROGRESSIVE Buy pricing.

            SellStepType = SellDeltaType.FIXED

            StartPrice = 55.55

            SellStepSize = 2

            QuantityMultiplier =  2

            MaxActiveBuy = 2

            Portfolio quantity = 19

            Expected Orders = 
            [
                OrderInfo(Settings.NewOrderId, symbol, 57.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 55.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 53.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 51.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 50.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 49.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 48.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 47.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 46.55, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 45.55, 1, True, True),
                OrderInfo(Settings.NewOrderId, symbol, 43.55, 1, True, False),
                OrderInfo(Settings.NewOrderId, symbol, 42.55, 2, False, False)
            ]

        """
        symbol = "XXXX"
        activeStockItem = ActiveStockItem(symbol=symbol)
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.StartPrice = 55.55
        activeStockItem.QuantityMultiplier = 2
        activeStockItem.MaxActiveBuy = 2

        portfolioQuantity = 19
        activeStockItem.PriceCoordinates = PriceCoordinates0
        
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 57.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 55.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 53.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 51.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 50.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 49.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 48.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 47.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 46.55, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 45.55, 1, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 43.55, 1, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 42.55, 2, False, False)
        ]

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioQuantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)

    def test_GeneratePossibleLimitOrders_BuyType_PROGRESSIVE_SellType_FIXED_PriceCoordinate1001(self):
        """ GeneratePossibleLimitOrders
            
            PROGRESSIVE Buy pricing.

            SellStepType = SellDeltaType.FIXED

            StartPrice = 56

            SellStepSize = 2

            QuantityMultiplier =  2

            MaxActiveBuy = 2

            Portfolio quantity = 220

            Expected Orders = 
            [
                OrderInfo(Settings.NewOrderId, symbol, 58, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 56, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 54, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 52, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 50, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 48, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 46, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 44, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 40, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 38, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 36, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 34, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 32, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 30, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 28, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 26, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 25, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 24, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 23, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 22, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 20, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 19, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 18, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 17, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 16, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 15, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 14, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 13, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 12, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 11, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 10, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 9, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 8, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 7.5, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 7, 4, True, True),
                OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
                OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
            ]

        """
        symbol = "XXXX"
        activeStockItem = ActiveStockItem(symbol=symbol)
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.StartPrice = 56
        activeStockItem.QuantityMultiplier = 2
        activeStockItem.MaxActiveBuy = 2

        portfolioQuantity = 220
        activeStockItem.PriceCoordinates = PriceCoordinates1001
        
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 58, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 56, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 54, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 52, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 50, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 48, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 46, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 44, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 40, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 38, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 36, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 34, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 32, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 30, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 28, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 26, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 25, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 24, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 23, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 22, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 20, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 19, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 18, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 17, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 16, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 15, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 14, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 13, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 12, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 11, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 10, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 9, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 8, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 7.5, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 7, 4, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
        ]

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioQuantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)
        
    def test_GeneratePossibleLimitOrders_BuyType_PROGRESSIVE_SellType_NEXTBUYPRICE_PriceCoordinate1001(self):
        """ GeneratePossibleLimitOrders
            
            PROGRESSIVE Buy pricing.

            SellStepType = SellDeltaType.NEXTBUYPRICE

            StartPrice = 56

            SellStepSize = 2 - This doesn't matter when SellStepType is NEXTBUYPRICE

            QuantityMultiplier =  2

            MaxActiveBuy = 2

            Portfolio quantity = 220

            Expected Orders = 
            [
                OrderInfo(Settings.NewOrderId, symbol, 58, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 56, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 54, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 52, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 50, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 48, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 46, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 44, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 40, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 38, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 36, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 34, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 32, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 30, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 28, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 26, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 24, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 23, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 22, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 20, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 19, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 18, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 17, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 16, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 15, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 14, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 13, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 12, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 11, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 10, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 9, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 8, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 7, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 6, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 5.5, 4, True, True),
                OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
                OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
            ]

        """
        symbol = "XXXX"
        activeStockItem = ActiveStockItem(symbol=symbol)
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.NEXTBUYPRICE
        activeStockItem.StartPrice = 56
        activeStockItem.QuantityMultiplier = 2
        activeStockItem.MaxActiveBuy = 2

        portfolioQuantity = 220
        activeStockItem.PriceCoordinates = PriceCoordinates1001
        
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 58, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 56, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 54, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 52, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 50, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 48, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 46, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 44, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 40, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 38, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 36, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 34, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 32, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 30, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 28, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 26, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 24, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 23, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 22, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 20, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 19, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 18, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 17, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 16, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 15, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 14, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 13, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 12, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 11, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 10, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 9, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 8, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 7, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 6, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 5.5, 4, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
        ]

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioQuantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)

    def test_GeneratePossibleLimitOrders_BuyType_PROGRESSIVE_SellType_PERCENTAGE_PriceCoordinate1001(self):
        """ GeneratePossibleLimitOrders
            
            PROGRESSIVE Buy pricing.

            SellStepType = SellDeltaType.PERCENTAGE

            StartPrice = 56

            SellStepSize = 5 - This is the percentage when SellStepType is PERCENTAGE

            QuantityMultiplier =  2

            MaxActiveBuy = 2

            Portfolio quantity = 220

            Expected Orders = 
            [
                OrderInfo(Settings.NewOrderId, symbol, 58.8, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 56.7, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 54.6, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 52.5, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 50.4, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 48.3, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 46.2, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 44.1, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 39.9, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 37.8, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 35.7, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 33.6, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 31.5, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 29.4, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 27.3, 2, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 25.2, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 24.15, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 23.1, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 22.05, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 19.95, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 18.9, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 17.85, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 16.8, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 15.75, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 14.7, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 13.65, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 12.6, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 11.55, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 10.5, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 9.45, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 8.4, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 7.35, 8, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 6.3, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 5.78, 20, False, True),
                OrderInfo(Settings.NewOrderId, symbol, 5.25, 4, True, True),
                OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
                OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
            ]

        """
        symbol = "XXXX"
        activeStockItem = ActiveStockItem(symbol=symbol)
        activeStockItem.SellStepSize = 5
        activeStockItem.SellStepType = SellDeltaType.PERCENTAGE
        activeStockItem.StartPrice = 56
        activeStockItem.QuantityMultiplier = 2
        activeStockItem.MaxActiveBuy = 2

        portfolioQuantity = 220
        activeStockItem.PriceCoordinates = PriceCoordinates1001
        
        expectedLimitOrders:List[OrderInfo] = [
            OrderInfo(Settings.NewOrderId, symbol, 58.8, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 56.7, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 54.6, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 52.5, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 50.4, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 48.3, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 46.2, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 44.1, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 42, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 39.9, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 37.8, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 35.7, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 33.6, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 31.5, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 29.4, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 27.3, 2, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 25.2, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 24.15, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 23.1, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 22.05, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 21, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 19.95, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 18.9, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 17.85, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 16.8, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 15.75, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 14.7, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 13.65, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 12.6, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 11.55, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 10.5, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 9.45, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 8.4, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 7.35, 8, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 6.3, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 5.78, 20, False, True),
            OrderInfo(Settings.NewOrderId, symbol, 5.25, 4, True, True),
            OrderInfo(Settings.NewOrderId, symbol, 5, 16, True, False),
            OrderInfo(Settings.NewOrderId, symbol, 4.5, 20, False, False),
        ]

        possibleLimitOrders:List[OrderInfo] = self.manageOrdersHelpers.GeneratePossibleLimitOrders(activeStockItem, portfolioQuantity)

        self.assertSequenceEqual(expectedLimitOrders, possibleLimitOrders)


if __name__ == '__main__':
    unittest.main()
