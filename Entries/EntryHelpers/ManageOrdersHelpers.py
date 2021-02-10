from decimal import Decimal
from typing import List

from BusinessModels.ActiveStockItem import ActiveStockItem
from BusinessModels.OrderInfo import OrderInfo
from BusinessModels.PriceCoordinate import BuyDeltaType, PriceCoordinate
from BusinessModels.SellDeltaType import SellDeltaType
from BusinessModels.Settings import Settings


class ManageOrdersHelpers:
    """ This is a very important class in the application used to generate/calculate the orders 
        and quantities for a given stock item. It also contains functions to calculate the 
        maximum investment for a given startprice and pricecoordinates.

        Attributes:

        Settings - The settings of the system.

        Methods:

        GetBuyPriceFromSellPrice - Gets the buy price of a given sell price for a stock item.

        GetSellPrice - Gets the sell price from a given buy price and stock item.

        GetNextLimitPrice - Gets the next limit price(backwards or forwards) from the current price using
        the startprice and pricecoordinates.

        GetQuantity - Gets the quantity associated with a stock item at a given price.

        CalculateMaxInvestment - Calculates the Maximum invenstment for a given startprice and pricecoordinates also taking into
        consideration quantity multiplier.

        GeneratePossibleLimitOrders - Generates the possible limit orders(both BUY and SELL) for a given stock item 
        and portfolio quantity of the stock item.


    """

    def __init__(self, settings:Settings):
        """ Initialization method.
        """
        self.Settings = settings        

    def GetBuyPriceFromSellPrice(self, activeStockItem:ActiveStockItem, sellPrice:float) -> float:
        """ Gets a buy price from sell price using the stock item.
            The buy price is calculated using the SellStepType of the stock item.

            SellStepType is NEXTBUYPRICE return next limit price(backwards).

            SellStepType is PERCENTAGE return (sellPrice / (1 + (activeStockItem.SellStepSize * 0.01))

            SellStepType is FIXED return sellPrice - activeStockItem.SellStepSize

            Please look at the documentation of SellStepSize of ActiveStockItem for more details.

            Parameters:

            activeStockItem:ActiveStockItem - Stock item details.

            sellPrice:float - The sell price for which we need the buy price.

            Returns:

            Buy price of the given sell price and stock item.
        """

        if(activeStockItem.SellStepType == SellDeltaType.NEXTBUYPRICE):
            # Return the next(backward) buy price.
            return self.GetNextLimitPrice(activeStockItem.StartPrice, sellPrice, 
                                                activeStockItem.PriceCoordinates, True) 
        elif(activeStockItem.SellStepType == SellDeltaType.FIXED):
            # return (sellPrice - SellStepSize).
            return round(sellPrice - activeStockItem.SellStepSize, self.Settings.FloatRoundPrecision)
        elif(activeStockItem.SellStepType == SellDeltaType.PERCENTAGE):
            # return sellPrice / (1 + (activeStockItem.SellStepSize * 0.01)).
            return round(sellPrice / (1 + (activeStockItem.SellStepSize * 0.01)), self.Settings.FloatRoundPrecision)
        else:
            raise Exception(f"UnSupported SellStepType - {activeStockItem.SellStepType}")

    def GetSellPrice(self, activeStockItem:ActiveStockItem, currentBuyPrice:float) -> float:
        """ Returns the Sell Price for a given Buy Price.

            If SellStepType is NEXTBUYPRICE return next limit price(forward).

            If SellStepType is FIXED return (BuyPrice + SellStepSize).

            If SellStepType is PERCENTAGE return (currentBuyPrice * (1 + (activeStockItem.SellStepSize * 0.01))

            Please look at the documentation of SellStepSize of ActiveStockItem for more details.

            Parameters:

            activeStockItem:ActiveStockItem - The stock item information.

            currentBuyPrice:float - The Buy price for which we need Sell Price.

            Returns:

            Sell price for the given buy price and stock item.

        """    
        if(activeStockItem.SellStepType == SellDeltaType.NEXTBUYPRICE):
            # Return the next(forward) buy price.
            return self.GetNextLimitPrice(activeStockItem.StartPrice, currentBuyPrice, 
                                                activeStockItem.PriceCoordinates, False) 
        elif(activeStockItem.SellStepType == SellDeltaType.FIXED):
            # return (BuyPrice + SellStepSize).
            return round(currentBuyPrice + activeStockItem.SellStepSize, self.Settings.FloatRoundPrecision)
        elif(activeStockItem.SellStepType == SellDeltaType.PERCENTAGE):
            # return BuyPrice + (SellStepSize percentage of BuyPrice).
            return round(currentBuyPrice * (1 + (activeStockItem.SellStepSize * 0.01)), self.Settings.FloatRoundPrecision)
        else:
            raise Exception(f"UnSupported SellStepType - {activeStockItem.SellStepType}")

    def GetNextLimitPrice(self, startPrice:Decimal, currentPrice:Decimal, priceCoordinates:List[PriceCoordinate], 
                                isPrevious:bool = True) -> float:
        """ Returns the next limit price. If isPrevious is True backward price is returned else 
            forward price is returned.

            Parameters:

            startPrice:Decimal - Start price of the stock. We need start price to traverse backwards.

            currentPrice:Decimal - The price from which you need the next price.

            priceCoordinates:List[PriceCoordinate] - Price coordinates.

            isPrevious:bool - If True backward price is returned else 
            forward price is returned.

            Returns:

            Next limit price. Backwards or Forward based on isPrevious parameter.

        """

        # Sort the price coordinates in the descending order of StartPrice.
        priceCoordinates.sort(key= lambda x:x.StartPrice, reverse=True)

        if isPrevious is True:
            for coordinate in priceCoordinates:
                # Find the coordinate to which the price belongs.
                if(currentPrice >= coordinate.StartPrice): 
                    # calculate the delta.
                    delta:Decimal = coordinate.FixedBuyDelta          
                    if(coordinate.BuyDeltaType == BuyDeltaType.MULTIPLIER):
                        delta = int(currentPrice / coordinate.StartPrice) + 1      
                    # calculate and return the next price(backwards).              
                    previousPrice = round(currentPrice - delta, self.Settings.FloatRoundPrecision)
                    return previousPrice
        else:
            # If current price is start price.
            if(currentPrice == startPrice):
                # Find the right coordinate, calculate detla and add it to currentBuyPrice.
                for coordinate in priceCoordinates:
                    if(currentPrice >= coordinate.StartPrice): 
                        delta = coordinate.FixedBuyDelta
                        if(coordinate.BuyDeltaType == BuyDeltaType.MULTIPLIER):
                            delta = int(currentPrice / coordinate.StartPrice) + 1
                        nextPrice = round(currentPrice + delta, self.Settings.FloatRoundPrecision)
                        return nextPrice

            # Current price cannot be greater than start price.
            price = startPrice  
            while True:
                # We traverse backwards from the start price.
                # Get the previous price.
                previousPrice = self.GetNextLimitPrice(startPrice, price, priceCoordinates, True)
                # If the previous price is current price. We found our next price(forward) which is
                # avaiable in price variable.
                if(previousPrice == currentPrice):
                    return price
                price = previousPrice

        return 0
        
    def GetQuantity(self, currentPrice:Decimal, priceCoordinates:List[PriceCoordinate]) -> int:
        """ Gets the quantity for a given price using the price coordinates.

            Parameters:

            currentPrice:Decimal - Price.

            priceCoordinates:List[PriceCoordinate] - Price coordinates of the stock item.

            Returns:

            int - Quantity for the given price and price coordinates.

        """

        # Sort the price coordinates in the descending order of StartPrice.
        priceCoordinates.sort(key= lambda x:x.StartPrice, reverse=True)

        # Find the coordinate and return its quantity.
        for coordinate in priceCoordinates:
            if(currentPrice >= coordinate.StartPrice):
                return coordinate.Quantity
        return 0

    def CalculateMaxInvestment(self, startPrice:Decimal, priceCoordinates:List[PriceCoordinate], 
                                    quantityMultiplier:int) -> float:
        """ Calculates the maximum investment for a given start price, pricecoordinates and 
            quantity multiplier. Starts from the start price, goes backwards and at each buy price
            calculates the investment and adds to the total investment.

            Parameters:

            startPrice:Decimal - The start price of the stock.

            priceCoordinates:List[PriceCoordinate] - Price coordinates associated with the stock.

            quantityMultiplier:int - Quantity multiplier.

            Returns:

            Float - Maximum investment.

        """

        currentPrice:Decimal = startPrice
        nextPrice:Decimal = 0
        currentTotal:Decimal = 0
        
        while True:  
            # At each price, get quantity      
            quantity = self.GetQuantity(currentPrice, priceCoordinates)
            # Get the next(backwards) price.
            nextPrice = self.GetNextLimitPrice(startPrice, currentPrice, priceCoordinates, True)
            if(currentPrice <= 0):
                break        

            # Add to the tracking total.
            currentTotal = round(currentTotal + currentPrice * quantity * quantityMultiplier, self.Settings.FloatRoundPrecision)

            # Set the price to next(backwards) price and continue the loop.
            currentPrice = nextPrice
        
        return currentTotal

    def GeneratePossibleLimitOrders(self, activeStockItem:ActiveStockItem, portfolioPositionQuantity:int) -> List[OrderInfo]:
        """ Generates the possible limit orders for the given stock item and portfolio quantity.
            Based on the number of stocks in the portfolio the SELL orders are generated and 
            based on the MaxActiveBuy the BUY orders are generated.

            Parameters:

            activeStockItem:ActiveStockItem - The stock item of the stock.

            portfolioPositionQuantity:int - Number of stocks in the portfolio.

            Return:

            List[OrderInfo] - Limit orders.

        """

        # Placeholder OrderId.
        orderIdNew = Settings.NewOrderId
        limitOrders:List[OrderInfo] = []

        # Initialize to start price.
        limitPrice = activeStockItem.StartPrice

        # Local price coordinates variable sorted by startprice.
        priceCoordinates:List[PriceCoordinate] = activeStockItem.PriceCoordinates
        priceCoordinates.sort(key= lambda x:x.StartPrice, reverse=True)

        quantity:int = 0 
        totalQuantity:int = 0

        # Get the quantity at the startprice.
        quantity = self.GetQuantity(limitPrice, priceCoordinates) * activeStockItem.QuantityMultiplier
        
        # Track if first BUY order is partial.
        isFirstBuyOrderPartial = False

        # Generate SELL orders.
        while True:
            totalQuantity = totalQuantity + quantity

            # Total quantity exceeds portfolio quantity.
            # Check if there is a partial order.
            if(totalQuantity > portfolioPositionQuantity):
                quantityDelta = totalQuantity - portfolioPositionQuantity

                # No partial order break.
                if(quantityDelta == quantity):
                    break

                # There is a partial order. Get the sell price for the limit price
                # and generate SELL order for the partial quantity.
                price = self.GetSellPrice(activeStockItem, limitPrice) 
                limitOrders.append(OrderInfo(orderIdNew, activeStockItem.Symbol,
                    price, quantity - quantityDelta, True, True)) 

                # First BUY order is partial.
                isFirstBuyOrderPartial = True

                # Set the quantity to the remaining quantity, so that BUY
                # order is generated for the remaining quantity.
                quantity = quantityDelta
                break

            # Get the sell price. Generate SELL order.
            price = self.GetSellPrice(activeStockItem, limitPrice) 
            limitOrders.append(OrderInfo(orderIdNew, activeStockItem.Symbol,
                    price, quantity, False, True)) 

            # Get next limit price(backwards) and it's quantity.
            limitPrice = self.GetNextLimitPrice(activeStockItem.StartPrice, limitPrice, 
                                            priceCoordinates, True)
            quantity = self.GetQuantity(limitPrice, priceCoordinates) * activeStockItem.QuantityMultiplier

        # Generate BUY orders.
        for i in range(activeStockItem.MaxActiveBuy):
            
            # Add BUY order. isFirstBuyOrderPartial = True => Partial Order
            limitOrders.append(OrderInfo(orderIdNew, activeStockItem.Symbol, 
                    limitPrice, quantity, isFirstBuyOrderPartial, False))

            # We already handled first BUY, so set this back to False.
            isFirstBuyOrderPartial = False

            # Get next price(backwards) and quantity.
            limitPrice = self.GetNextLimitPrice(activeStockItem.StartPrice, limitPrice, 
                                            priceCoordinates, True)
            quantity = self.GetQuantity(limitPrice, priceCoordinates) * activeStockItem.QuantityMultiplier

        return limitOrders

