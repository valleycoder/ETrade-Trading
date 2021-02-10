from typing import List

from BusinessModels.OrdersResponse import OrderDetail


class PreviewOrderInput:
    """ Inorder to place an order first you have to preview the order. Once preview order is verified then
        you have to pass the same information to the place order request. This information is maintained
        in this class object.

        Attribute:

        OrderType - We only support EQ order type.

        ClientOrderId - Unique Id.

        Order - Order detail list. We need only one Order detail because we only support EQ order type.

    """
    def __init__(self):
        self.OrderType:str = ""
        self.ClientOrderId:str = ""
        self.Order:List[OrderDetail] = []
        