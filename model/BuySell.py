from model.FTX_Class import FtxClient
from time import sleep


class BuySell:
    """ Buys and Sells orders and gives account information """
    def __init__(self, coin, values):
        self.pair = self.create_pair(coin)
        if len(values) == 2:
            self.client = FtxClient(api_key=values[0],
                                    api_secret=values[1].strip())
        else:
            self.client = FtxClient(api_key=values[0],
                                    api_secret=values[1],
                                    sub_account_name=values[2].strip())

    def buy_sell_limit_rebalance(self, side, size):
        """ places a limit order at the top of the orderbook. When the order is not at the top of the orderbook
         any more closes the order and places a new order at the top. Does this until the order is filled """
        order = self.place_order_at_top_of_list(side, size)
        bid_price = order['price']
        order_id = self.get_order_id(order)
        while True:
            # order is filled
            if self.get_order_status(order_id) == "closed" and self.get_filled_size(order_id) > 0:
                return self.get_order(order_id)
            new_bid_price = self.get_bid_ask(side)
            if side == "buy":
                if new_bid_price > bid_price:
                    response = self.cancel_and_place_order(order_id, side, size)
                    order_id = response[0]
                    bid_price = response[1]
            else:
                if new_bid_price < bid_price:
                    response = self.cancel_and_place_order(order_id, side, size)
                    order_id = response[0]
                    bid_price = response[1]
            sleep(0.25)

    def cancel_and_place_order(self, order_id, side, size):
        """ cancels order and places a new one """
        response = self.cancel_order(order_id)
        if response == "Order already closed":
            return order_id, 0
        else:
            order = self.place_order_at_top_of_list(side, size)
            return order['id'], order['price']

    def cancel_order(self, order_id):
        try:
            return self.client.cancel_order(order_id)
        except Exception as e:
            if str(e) == "Order already closed":
                return "Order already closed"
            else:
                raise

    def get_order_status(self, order_id):
        """ returns the current status of the order """
        status = self.client.get_order_status(order_id)
        status1 = status['status']
        return status1

    def get_order(self, order_id):
        """ returns current information about the order """
        return self.client.get_order_status(order_id)

    def get_filled_size(self, order_id):
        """ returns the filled Size of an order """
        status = self.client.get_order_status(order_id)
        filled = status['filledSize']
        return filled

    def get_avg_fill_price(self, order_id):
        """ returns the filled price of an order """
        status = self.client.get_order_status(order_id)
        return status['avgFillPrice']

    @staticmethod
    def get_order_id(order):
        return order['id']

    def place_order_at_top_of_list(self, side, size):
        """ places an order at the top of the orderbook. uses the post only order type which can only buy as maker.
        taker orders get canceled instead."""
        bid_price = self.get_bid_ask(side)
        order = self.buy_sell_limit_never_taker(bid_price, side, size)
        order_id = self.get_order_id(order)
        status = self.get_order_status(order_id)
        while True:
            # order was cancelled
            if status == "closed" and self.get_filled_size(order_id) == 0:
                bid_price = self.get_bid_ask(side)
                order = self.buy_sell_limit_never_taker(bid_price, side, size)
                order_id = self.get_order_id(order)
                status = order['status']
            # order was filled
            if status == "closed" and self.get_filled_size(order_id) > 0:
                return order
            # order is at top of list
            if status == "open":
                return order
            # order it not yet processed
            if status == "new":
                order_id = self.get_order_id(order)
                status = self.get_order_status(order_id)
            sleep(0.1)

    def buy_sell_market(self, side, size):
        """ places a market order """
        return self.client.place_order(self.pair, side, size, None, "market")

    def buy_sell_limit_never_taker(self, price, side, size):
        """ places a post only limit order """
        return self.client.place_order(self.pair, side, size, price, "limit", False, False, True)

    def buy_sell_limit(self, side, size):
        """ places a post only limit order """
        bid_price = self.get_bid_ask(side)
        return self.client.place_order(self.pair, side, size, bid_price, "limit")

    def price(self):
        return self.get_price()

    def get_price(self):
        """ returns the price of the coin """
        response = self.client.get_single_future(self.pair)
        price = response['mark']
        return price

    def get_bid_ask(self, side):
        """ returns the highest bid or ask price """
        if side == "buy":
            return self.get_bid()
        else:
            return self.get_ask()

    def get_bid(self):
        response = self.client.get_single_future(self.pair)
        bid = response['bid']
        return bid

    def get_ask(self):
        response = self.client.get_single_future(self.pair)
        ask = response['ask']
        return ask

    @staticmethod
    def create_pair(coin):
        return coin + "-PERP"

    def has_enough_collateral(self, dollar):
        """ checks if dollar is smaller than the available account balance """
        account_info = self.client.get_future_account_info()
        free_collateral = float(account_info['freeCollateral'])
        return dollar < free_collateral

    def get_account_info(self):
        """ returns information about the account """
        return self.client.get_future_account_info()
