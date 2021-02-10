from typing import List

from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate

"""
    Some sample data for the Tests.
"""

# Sample PriceCoordinates1001
PriceCoordinates1001:List[PriceCoordinate] = []
PriceCoordinates1001.append(PriceCoordinate(startPrice=50,quantity=1, buyDeltaType=BuyDeltaType.MULTIPLIER, fixedBuyDelta=0))
PriceCoordinates1001.append(PriceCoordinate(startPrice=25,quantity=1, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=2))
PriceCoordinates1001.append(PriceCoordinate(startPrice=7,quantity=4, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=1))
PriceCoordinates1001.append(PriceCoordinate(startPrice=0,quantity=10, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.5))
