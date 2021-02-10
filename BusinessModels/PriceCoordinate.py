from decimal import Decimal
from enum import Enum, unique


@unique
class BuyDeltaType(Enum):
    """ Represents the buy interval type used to determine the Buy prices. The next price is 
        always backwards from the start price of the given stock.

        FIXED - Buy interval is fixed starting from the coordinate to the next available coordinate.

        MULTIPLIER - Buy interval(backwards) is int(LimitPrice / startPrice) + 1 starting from the 
        coordinate to the next available coordinate.

    """
    FIXED = 1
    MULTIPLIER = 2


class PriceCoordinate:
    """ Used to represent the variable price/quantity in the system. Price is always backwards from
        the start price of the stock. The quantity is fixed between one coordinate to next available 
        coordinate. Next price(backwards) is based on the DeltaType.

        At a given price, you can calculate the next(backwards) price by using the BuyDeltaType
        and FixedBuyDelta values. At a given price, you can calculate the quantity by finding the 
        coordinate to which the given price falls.

        Example:

        PriceCoordinates1:List[PriceCoordinate] = []

        PriceCoordinates1.append(PriceCoordinate(startPrice=50,quantity=1, buyDeltaType=BuyDeltaType.MULTIPLIER, fixedBuyDelta=0))
        PriceCoordinates1.append(PriceCoordinate(startPrice=25,quantity=1, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=1))
        PriceCoordinates1.append(PriceCoordinate(startPrice=15,quantity=2, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.5))
        PriceCoordinates1.append(PriceCoordinate(startPrice=7,quantity=4, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.25))
        PriceCoordinates1.append(PriceCoordinate(startPrice=0,quantity=10, buyDeltaType=BuyDeltaType.FIXED, fixedBuyDelta=0.1))


        Using the above PriceCoordinates1 list.

        For Price 71 -> Next Price(always backwards) is (71 - (int(71/50) + 1)), which is 69. MULTIPLIER BuyDeltaType used here.
        For Price 71 -> Quantity is 1.

        For Price 50 -> Next Price(always backwards) is (50 - (int(50/50) + 1)), which is 48. MULTIPLIER BuyDeltaType used here.
        For Price 50 -> Quantity is 1, which is quantity of the PriceCooridinate with StartPrice 50.
        For Price 48 -> Quantity is 1, which is quantity of the PriceCoordinate with StartPrice 48.

        For Price 14.5 -> Next Price is (14.5 - 0.25), which is 14.25. FIXED BuyDeltaType used here.
        For Price 14.25 -> Quantity is 4, which is the quantity of the PriceCoordinate with StartPrice 7.


        Attributes:

        StartPrice - Start price of the coordinate.

        Quantity - Quantity within this coordinate range. Quantity will be same from this coordinate
        to the next available coordinate.

        BuyDeltaType - Either fixed or multplier.

        FixedBuyDelta - If BuyDeltaType is fixed, use this field to calculate the next backward price.

    """
    def __init__(self, startPrice:Decimal, quantity:int, 
                    buyDeltaType:BuyDeltaType = BuyDeltaType.FIXED, 
                    fixedBuyDelta:Decimal = 0
                ):
        self.StartPrice:Decimal = startPrice
        self.Quantity:int = quantity
        self.BuyDeltaType:BuyDeltaType = buyDeltaType
        self.FixedBuyDelta:Decimal = fixedBuyDelta

