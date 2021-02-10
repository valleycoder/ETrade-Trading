import os
import sys
import unittest
from pathlib import Path
from typing import List

sys.path.append(str(Path(os.getcwd()).parent))

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType
from BusinessModels.Settings import Settings
from Entries.EntryHelpers.ManageOrdersHelpers import ManageOrdersHelpers


class tests_ManageOrdersHelpers_GetBuyPriceFromSellPrice(unittest.TestCase):
    """ Tests related to GetBuyPriceFromSellPrice method of ManagerOrdersHelpers class.
    """

    def setUp(self):
        # Initialize the object.
        self.manageOrdersHelpers = ManageOrdersHelpers(Settings())

    def tearDown(self):
        pass

    def test_GetBuyPriceFromSellPrice_SellDeltaType_FIXED_SellPrice_Is_StartPrice(self):
        """ GetBuyPriceFromSellPrice

            SellPrice is same as StartPrice.

            Flat pricing model

            SellPrice = StartPrice = 12.55

            SellStepSize = 1 

            Expected BuyPrice is 11.55
        """
        activeStockItem = ActiveStockItem(symbol="XXXX")
        quantity = 1
        sellPrice = 12.55
        buyStepSize = 1
        expectedBuyPrice = 11.55
        activeStockItem.SellStepSize = 1
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.StartPrice = sellPrice
        activeStockItem.QuantityMultiplier = 1
                
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        returnedBuyPrice = self.manageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, sellPrice)
        self.assertEqual(expectedBuyPrice, returnedBuyPrice)

    def test_GetBuyPriceFromSellPrice_SellDeltaType_FIXED_SellPrice_Is_LessThan_StartPrice(self):
        """ GetBuyPriceFromSellPrice

            SellPrice is less than StartPrice.

            Flat pricing model

            SellPrice = 10.55

            StartPrice = 12.55

            SellStepSize = 2

            Expected BuyPrice is 8.55
        """
        activeStockItem = ActiveStockItem(symbol="XXXX")
        quantity = 1
        sellPrice = 10.55
        buyStepSize = 0.50
        expectedBuyPrice = 8.55
        activeStockItem.StartPrice = 12.55
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.FIXED
        activeStockItem.QuantityMultiplier = 1
        
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        returnedBuyPrice = self.manageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, sellPrice)
        self.assertEqual(expectedBuyPrice, returnedBuyPrice)

    def test_GetBuyPriceFromSellPrice_SellDeltaType_NEXTBUYPRICE_SellPrice_Is_LessThan_StartPrice(self):
        """ GetBuyPriceFromSellPrice

            SellPrice is less than StartPrice.

            Flat pricing model

            BuyStepSize = 0.5

            SellPrice = 10.55

            StartPrice = 12.55

            SellStepSize = 2 - when SellDeltaType is NEXTBUYPRICE, SellStepSize must be ignored.

            Expected BuyPrice is 10.05

        """
        activeStockItem = ActiveStockItem(symbol="XXXX")
        quantity = 1
        sellPrice = 10.55
        buyStepSize = 0.50
        expectedBuyPrice = 10.05
        activeStockItem.StartPrice = 12.55
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.NEXTBUYPRICE
        activeStockItem.QuantityMultiplier = 1
        
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        returnedBuyPrice = self.manageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, sellPrice)
        self.assertEqual(expectedBuyPrice, returnedBuyPrice)

    def test_GetBuyPriceFromSellPrice_SellDeltaType_NEXTBUYPRICE_SellPrice_Is_MoreThan_StartPrice(self):
        """ GetBuyPriceFromSellPrice

            SellPrice is more than StartPrice.

            Flat pricing model

            BuyStepSize = 0.5

            SellPrice = 13.05

            StartPrice = 12.55

            SellStepSize = 2 - when SellDeltaType is NEXTBUYPRICE, SellStepSize must be ignored.

            Expected BuyPrice is 12.55

        """
        activeStockItem = ActiveStockItem(symbol="XXXX")
        quantity = 1
        sellPrice = 13.05
        buyStepSize = 0.50
        expectedBuyPrice = 12.55
        activeStockItem.StartPrice = 12.55
        activeStockItem.SellStepSize = 2
        activeStockItem.SellStepType = SellDeltaType.NEXTBUYPRICE
        activeStockItem.QuantityMultiplier = 1
        
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        returnedBuyPrice = self.manageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, sellPrice)
        self.assertEqual(expectedBuyPrice, returnedBuyPrice)

    def test_GetBuyPriceFromSellPrice_SellDeltaType_PERCENTAGE_SellPrice_Is_LessThan_StartPrice(self):
        """ GetBuyPriceFromSellPrice

            SellPrice is less than StartPrice.

            Flat pricing model

            BuyStepSize = 0.5

            SellPrice = 11.61

            StartPrice = 12.55

            SellStepSize = 10 - when SellDeltaType is PERCENTAGE, SellStepSize is % value.

            Expected BuyPrice is 10.55

        """
        activeStockItem = ActiveStockItem(symbol="XXXX")
        quantity = 1
        sellPrice = 11.61
        buyStepSize = 0.50
        expectedBuyPrice = 10.55
        activeStockItem.StartPrice = 12.55
        activeStockItem.SellStepSize = 10
        activeStockItem.SellStepType = SellDeltaType.PERCENTAGE
        activeStockItem.QuantityMultiplier = 1
        
        priceCoordinates:List[PriceCoordinate] = []
        priceCoordinates.append(PriceCoordinate(startPrice=0,quantity=quantity, 
                            buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=buyStepSize))
        activeStockItem.PriceCoordinates = priceCoordinates

        returnedBuyPrice = self.manageOrdersHelpers.GetBuyPriceFromSellPrice(activeStockItem, sellPrice)
        self.assertEqual(expectedBuyPrice, returnedBuyPrice)


if __name__ == '__main__':
    unittest.main()
