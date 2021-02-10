from typing import List

from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate

"""
    List of price coordinates in the system.

    Whenever you need to create a new price coordinate, create one here and name it appropriately.

    This application is very a specific application designed for a very small set of people who
    are also supposedly software developers. So the expectation is that it is the resposibility of the 
    script users to create the price coordiates manually.

    For PriceCoordinates0 - The ActiveItem quantity will be 0.
    For PriceCoordinates1 - The ActiveItem quantity will be -1.
    For PriceCoordinates2 - The ActiveItem quantity will be -2.
    For PriceCoordinates101 - The ActiveItem quantity will be -101.
    ...

    It's a convention based design.

    Please look at the documenation of the PriceCoordinate class for more details.

    Some rules to follow:

    - Make sure that the start prices don't overlap.
    - Make sure that fixedBuyDelta > 0 when buyDeltaType is BuyDeltaType.FIXED.

"""

PriceCoordinates0:List[PriceCoordinate] = []

PriceCoordinates0.append(PriceCoordinate(startPrice=50,quantity=1, buyDeltaType=BuyDeltaType.MULTIPLIER, fixedBuyDelta=0))
PriceCoordinates0.append(PriceCoordinate(startPrice=25,quantity=1, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=1))
PriceCoordinates0.append(PriceCoordinate(startPrice=15,quantity=2, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.5))
PriceCoordinates0.append(PriceCoordinate(startPrice=7,quantity=4, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.25))
PriceCoordinates0.append(PriceCoordinate(startPrice=0,quantity=10, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.1))
