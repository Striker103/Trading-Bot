from model.BuySell import BuySell
from model.MarketData import MarketData
from abc import abstractmethod


class Coin:
    """ Has the basic attributes which each coin has """
    def __init__(self, coin, dollar, current_price):
        # the name of the coin
        self.coin = coin
        # the dollar per trade
        self.dollar = round(float(dollar), 2)
        # the current price of the coin
        self.current_price = current_price

    def set_current_price(self, price):
        self.current_price = price


class ManuelTrading(Coin):
    """ Used the make manuel trades """
    def __init__(self, coin, dollar: float, order_type, min_order_size, account):
        super().__init__(coin, dollar, round(MarketData().get_price(coin), 2))
        # used the place orders and get account information
        self.place_order = BuySell(coin, account)
        # used to get market data
        self.market_data = MarketData()
        # the size of the order negative means short position and positive long position
        self.size = 0
        # the side of the order
        self.side = ""
        # true if size is 0
        self.to_delete = False
        # order type of this strategy
        self.order_type = order_type
        # the minimum order size of an order of this specific coin
        self.min_order_size = min_order_size

    def get_side(self):
        return self.side

    def get_round_size(self):
        """ returns the number of digits after the point in a float number """
        return int(str(self.min_order_size)[::-1].find('.') + 1)

    def get_position_value(self):
        """ returns the value of the open position in dollar """
        return self.market_data.get_price(self.coin) * abs(self.size)

    def set_order_type(self, order_type):
        self.order_type = order_type

    def calculate_quantity_to_buy(self, dollar):
        return float(dollar) / self.market_data.get_price(self.coin)

    def set_current_price(self, price):
        self.current_price = round(price, 2)

    def set_size(self, size):
        self.size = round(size, self.get_round_size())
        self.dollar = round(self.get_position_value(), 2)

    def get_size(self):
        return self.size

    def set_side(self, side):
        self.side = side

    def update_dollar(self):
        self.dollar = self.size * self.market_data.get_price(self.coin)
        self.dollar = round(self.dollar, 2)

    def close_position(self):
        """ places an order in the opposite side of the open order"""
        if self.order_type == "Market":
            if self.side == "long":
                self.place_order.buy_sell_market("sell", self.size)
            else:
                self.place_order.buy_sell_market("buy", abs(self.size))
        else:
            if self.side == "long":
                self.place_order.buy_sell_limit_rebalance("sell", self.size)
            else:
                self.place_order.buy_sell_limit_rebalance("buy", abs(self.size))

    def __str__(self):
        return ("coin:" + self.coin + ", current price:" + str(self.current_price) + ", position value:" +
                str(self.dollar) + ", size:" + str(abs(self.size)) + ", side:" + str(self.side) +
                ", order type:" + self.order_type)


class TradeParameters(Coin):
    """ Stores  basic attributes of all live and backtest strategies"""
    def __init__(self, coin, dollar, current_price, take_profit, stop_loss, time_frame, length):
        super().__init__(coin, dollar, current_price)
        # the value at which a position should be closed with a profit (in percent)
        self.take_profit = take_profit
        # the value at which a position should be closed with a loss (in percent)
        self.stop_loss = stop_loss
        # the price at which an order was placed
        self.enter_market_at_price = 0
        # the price at which the position was closed
        self.exit_market_at_price = 0
        # the time frame of the candles
        self.time_frame = time_frame
        # the number of candles to be taken into account for calculation of indicators
        self.length = length
        # the take profit price at which a position should be closed in dollar
        self.current_take_profit = 0
        # the stop loss price at which a position should be closed in dollar
        self.current_stop_loss = 0
        # number of winning trades
        self.win = 0
        # number of losing trades
        self.losses = 0
        # overall profit
        self.wins = 0
        # the fees in dollar when the current trade was opened
        self.open_fees = 0
        # the fees in dollar when the current trade was closed
        self.close_fees = 0
        # the end results of the backtest
        self.single_trade = []
        # the results of all trades
        self.trades = []
        # the size that was bought with the current trade
        self.quantity = 0
        # the profit of the current trade. a negative value means the trade had a stop loss
        self.trade_profit = 0
        # the time at which the current trade was opened
        self.trade_open_time = "a"
        # the time at which the current trade was closed
        self.trade_close_time = "b"
        # profit or loss depending on trade outcome
        self.success = "profit"
        # side of the trade
        self.side = "long"
        # True when a trade cycle is done. All values of this cycle are written to a new line of the csv file
        self.make_backtest_row = False

    def increment_wins(self):
        self.wins += 1

    def increment_losses(self):
        self.losses += 1

    def update_current_take_profit_long(self):
        self.current_take_profit = self.enter_market_at_price + (self.enter_market_at_price * (self.take_profit / 100))

    def update_current_stop_loss_long(self):
        self.current_stop_loss = self.enter_market_at_price - (self.enter_market_at_price * (self.stop_loss / 100))

    def update_current_take_profit_short(self):
        self.current_take_profit = self.enter_market_at_price - (self.enter_market_at_price * (self.take_profit / 100))

    def update_current_stop_loss_short(self):
        self.current_stop_loss = self.enter_market_at_price + (self.enter_market_at_price * (self.stop_loss / 100))

    def update_trade_profit_with_winning_trade(self):
        if self.enter_market_at_price > self.exit_market_at_price:
            self.trade_profit = ((self.enter_market_at_price - self.exit_market_at_price) * self.quantity -
                                 self.open_fees - self.close_fees)
        else:
            self.trade_profit = ((self.exit_market_at_price - self.enter_market_at_price) * self.quantity -
                                 self.open_fees - self.close_fees)

    def update_trade_profit_with_losing_trade(self):
        if self.enter_market_at_price > self.exit_market_at_price:
            self.trade_profit = ((-1) * (self.enter_market_at_price - self.exit_market_at_price) * self.quantity -
                                 self.open_fees - self.close_fees)
        else:
            self.trade_profit = ((-1) * ((self.exit_market_at_price - self.enter_market_at_price) * self.quantity) -
                                 self.open_fees - self.close_fees)

    def update_sum_of_profits(self):
        self.win = round(self.win + self.trade_profit, 2)

    def set_success(self, success):
        self.success = success

    def set_side(self, side):
        self.side = side

    def update_money_per_trade(self):
        self.dollar = round(self.dollar + self.trade_profit, 2)

    def update_market_exit_price(self):
        self.exit_market_at_price = self.current_price


class Live(TradeParameters):
    """ Stores the FSM logic """
    def __init__(self, coin, dollar, order_type, min_order_size, account, take_profit, stop_loss, time_frame,
                 length):
        super().__init__(coin, dollar, round(MarketData().get_price(coin), 2), take_profit, stop_loss, time_frame,
                         length)
        # used to get market data
        self.market_data = MarketData()
        # used to place orders
        self.place_order = BuySell(coin, account)
        # the size of the order
        self.size = 0
        # the order type of the strategy
        self.order_type = order_type
        # the minimum order size of an order of this specific coin
        self.min_order_size = min_order_size
        # response of the Exchange with data form last order
        self.last_order = 0

    def set_current_price(self, price):
        self.current_price = round(price, 2)

    def get_round_size(self):
        """ returns the number of digits after the point in a float number """
        return int(str(self.min_order_size)[::-1].find('.'))

    def set_order_type(self, order_type):
        self.order_type = order_type

    def calculate_quantity_to_buy(self):
        """ returns returns the size to buy """
        return self.dollar / self.market_data.get_price(self.coin)

    def update_market_enter_price(self):
        """ sets enter_market_at_price to the price at which an order was placed  """
        self.enter_market_at_price = self.place_order.get_avg_fill_price(self.last_order['id'])
        if not self.enter_market_at_price:
            self.enter_market_at_price = self.market_data.get_price(self.coin)

    def update_market_exit_price(self):
        """ sets enter_market_at_price to the price at which an order was placed  """
        self.exit_market_at_price = self.place_order.get_avg_fill_price(self.last_order['id'])
        if not self.enter_market_at_price:
            self.enter_market_at_price = self.market_data.get_price(self.coin)

    def get_current_price_of_coin(self):
        return self.market_data.get_price(self.coin)

    def place_specific_order(self, side):
        """ places an order """
        if self.order_type == "Market":
            self.place_market_order(side)
        else:
            self.place_limit_order(side)

    def place_market_order(self, side):
        order = self.place_order.buy_sell_market(side, self.calculate_quantity_to_buy())
        self.last_order = order
        self.size = self.size + order['size']

    def place_limit_order(self, side):
        order = self.place_order.buy_sell_limit_rebalance(side, self.calculate_quantity_to_buy())
        self.last_order = order
        self.size = self.size + order['size']

    def close_order(self, side):
        """ closes an order """
        if self.order_type == "Market":
            order = self.place_order.buy_sell_market(side, self.size)
            self.last_order = order
            self.size = 0
        else:
            order = self.place_order.buy_sell_limit_rebalance(side, self.size)
            self.last_order = order
            self.size = 0

    def enter_long(self):
        """ when the FSM enters long a long position is opened """
        # open position
        self.place_specific_order("buy")
        self.update_market_enter_price()
        self.update_current_take_profit_long()
        self.update_current_stop_loss_long()

    def enter_entry(self):
        pass

    def execute_long(self):
        """ as soon as the current price of the coin is bigger than take profit the fsm goes to entry
         if it is smaller than current stop loss the fsm goes to stop loss"""
        if self.current_price > self.current_take_profit:
            self.long_to_entry()
        if self.current_price < self.current_stop_loss:
            self.long_to_stop_loss()

    def exit_long(self):
        """ when the FSM exits long the long position is closed """
        # close position
        self.close_order("sell")
        self.update_market_exit_price()

    def enter_short(self):
        """ when the FSM enters short a short position is opened """
        # open position
        self.place_specific_order("sell")
        self.update_market_enter_price()
        self.update_current_take_profit_short()
        self.update_current_stop_loss_short()

    def execute_short(self):
        """ as soon as the current price of the coin is smaller than take profit the fsm goes to entry
        if it is bigger than current stop loss, the fsm goes to stop loss"""
        if self.current_price < self.current_take_profit:
            self.short_to_entry()
        if self.current_price > self.current_stop_loss:
            self.short_to_stop_loss()

    def exit_short(self):
        """ when the FSM exits short the short position is closed """
        # close position
        self.close_order("buy")
        self.update_market_exit_price()

    def enter_stop_loss(self):
        """ when a trade is closed because a stop loss is trigger this state is entered """
        pass

    def enter_done(self):
        """ when the user shuts down the strategy this state is entered """
        pass

    @abstractmethod
    def execute_entry(self):
        """ Has to be implemented be all child classes which inheritance this parent class. Handles the logic
        when a position should be opened """
        raise NotImplementedError

    @abstractmethod
    def execute_stop_loss(self):
        """ Has to be implemented be all child classes which inheritance this parent class. Handles the logic what
        happens if a stop loss order was executed. """
        raise NotImplementedError


class RsiLive(Live):
    """ Implements RSI strategy logic """
    def __init__(self, coin, dollar, order_type, min_order_size, account, take_profit, stop_loss, overbought,
                 oversold, time_frame, length):
        super().__init__(coin, dollar, order_type, min_order_size, account, take_profit, stop_loss, time_frame,
                         length)
        # the price at which a coin is overbought
        self.overbought = overbought
        # the price at which a coin is oversold
        self.oversold = oversold
        # the current rsi of the coin
        self.rsi = None
        self.last_rsi = -1

    def set_current_rsi(self, rsi):
        self.rsi = round(rsi, 2)

    def get_middle_of_overbought_oversold(self):
        return (self.overbought + self.oversold)/2

    def __str__(self):
        s1 = ("state:" + self.state + ", coin:" + self.coin + ", current price:" + str(self.current_price) +
              ", RSI:" + str(self.rsi) + ", dollar:" + str(self.dollar) + ", overbought:" + str(self.overbought) +
              ", oversold:" + str(self.oversold))
        if self.state == "long" or self.state == "short":
            if self.current_take_profit > 1:
                self.current_take_profit = round(self.current_take_profit, 2)
                self.current_stop_loss = round(self.current_stop_loss, 2)
            else:
                round(self.current_take_profit, 5)
                round(self.current_stop_loss, 5)
            s2 = (" take profit:" + str(self.current_take_profit) + ", stop loss:" + str(self.current_stop_loss))
        else:
            s2 = (" take profit:" + str(self.take_profit) + ", stop loss:" + str(self.stop_loss))
        return s1 + s2

    def execute_entry(self):
        """ when the rsi is smaller than the oversold value and the account has enough collateral a long position
         is opened. is the rsi is bigger than oversold a short position is opened"""
        if self.rsi < self.oversold:
            if self.place_order.has_enough_collateral(self.dollar):
                self.entry_to_long()
        if self.rsi > self.overbought:
            if self.place_order.has_enough_collateral(self.dollar):
                self.entry_to_short()

    def execute_stop_loss(self):
        """ when a stop loss was triggered the bots waits until the market has a "normal" rsi """
        middle = self.get_middle_of_overbought_oversold()
        if self.last_rsi <= middle <= self.rsi or self.rsi >= middle >= self.last_rsi:
            self.stop_loss_to_entry()
        self.last_rsi = self.rsi


class MALive(Live):
    """ Implements Ma strategy logic """
    def __init__(self, coin, dollar, order_type, min_order_size, account, take_profit, stop_loss,
                 time_frame, length):
        super().__init__(coin, dollar, order_type, min_order_size, account, take_profit, stop_loss, time_frame,
                         length)
        self.ma = None
        self.last_price = round(MarketData().get_price(coin), 2)

    def set_current_ma(self, ma):
        self.ma = round(ma, 2)

    def __str__(self):
        s1 = ("state:" + self.state + ", coin:" + self.coin + ", current price:" + str(self.current_price) +
              ", last price:" + str(self.last_price) + ", MA:" + str(self.ma) + ", dollar:" + str(self.dollar))
        if self.state == "long" or self.state == "short":
            if self.current_take_profit > 1:
                self.current_take_profit = round(self.current_take_profit, 2)
                self.current_stop_loss = round(self.current_stop_loss, 2)
            else:
                round(self.current_take_profit, 5)
                round(self.current_stop_loss, 5)
            s2 = (" take profit:" + str(self.current_take_profit) + ", stop loss:" + str(self.current_stop_loss))
        else:
            s2 = (" take profit:" + str(self.take_profit) + ", stop loss:" + str(self.stop_loss))
        return s1 + s2

    def execute_entry(self):
        """ when the current candle breaks through the ma from below a long position is opened. When it breaks
        through from above a short position is opened"""
        if float(self.last_price) < float(self.ma) < float(self.current_price):
            if self.place_order.has_enough_collateral(self.dollar):
                self.entry_to_long()
        elif float(self.last_price) > float(self.ma) > float(self.current_price):
            if self.place_order.has_enough_collateral(self.dollar):
                self.entry_to_short()

    def execute_stop_loss(self):
        """ When a stop loss is triggerd nothing should happen the strategy just goes back to entry and waits for the
        next opportunity """
        self.stop_loss_to_entry()


class Backtest(TradeParameters):
    """ Stores the FSM logic """
    def __init__(self, coin, dollar, take_profit, stop_loss, file_name, days, fees, single_backtest, time_frame,
                 length):
        super().__init__(coin, dollar, 0, take_profit, stop_loss, time_frame, length)

        # True while the Backtest is calculating
        self.calculating = True
        # The start time of the current candle market data
        self.current_time = 0
        # the csv file name at which the backtest is stored
        self.file_name = file_name
        # number of days of the backtest
        self.days = days
        # fees per trade
        self.fees = fees
        # True if it is not an interval backtest
        self.single_backtest = single_backtest
        # True while past candles are fetched
        self.fetching_market_data = True

    def set_current_time(self, time):
        self.current_time = time

    def update_market_enter_price(self):
        self.enter_market_at_price = self.current_price

    def append_single_trade(self, value):
        self.single_trade.append(value)

    def update_quantity(self):
        """ updates the size that is bought with this trade """
        self.quantity = self.dollar / self.enter_market_at_price

    def update_open_fees(self):
        self.open_fees = float(self.enter_market_at_price) * float(self.quantity) * 0.01 * float(self.fees)

    def update_close_fees(self):
        self.close_fees = float(self.exit_market_at_price) * float(self.quantity) * 0.01 * float(self.fees)

    def update_trade_open_time(self):
        self.trade_open_time = self.current_time

    def update_trade_close_time(self):
        self.trade_close_time = self.current_time

    def append_trade_settings(self):
        self.single_trade.append(self.coin)
        self.single_trade.append(self.dollar)
        self.single_trade.append(self.time_frame)
        self.single_trade.append(self.length)

    def append_trade_outcome(self):
        """ a new line for the csv file with all trade data of this trade """
        self.single_trade.append(self.take_profit)
        self.single_trade.append(self.stop_loss)
        self.single_trade.append(self.days)
        self.single_trade.append(round(float(self.current_take_profit), 2))
        self.single_trade.append(round(float(self.current_stop_loss), 2))
        self.single_trade.append(self.side)
        self.single_trade.append(self.trade_open_time)
        self.single_trade.append(round(float(self.enter_market_at_price), 2))
        self.single_trade.append(round(float(self.open_fees), 2))
        self.single_trade.append(round(float(self.quantity), 2))
        self.single_trade.append(self.trade_close_time)
        self.single_trade.append(round(float(self.exit_market_at_price), 2))
        self.single_trade.append(round(float(self.close_fees), 2))
        self.single_trade.append(self.success)
        self.single_trade.append(self.wins)
        self.single_trade.append(self.losses)
        self.single_trade.append(round(float(self.trade_profit), 2))
        self.single_trade.append(self.win)

        self.trades.append(self.single_trade)

    def append_single_trade_outcome(self):
        self.single_trade.append(self.take_profit)
        self.single_trade.append(self.stop_loss)
        self.single_trade.append(self.days)
        self.single_trade.append(self.wins)
        self.single_trade.append(self.losses)
        self.single_trade.append(self.win)

    def make_file_line(self):
        """ sets attributes at the end of trade cycle """
        self.set_success("profit")
        self.increment_wins()
        self.update_market_exit_price()
        self.update_close_fees()
        self.update_trade_close_time()
        self.update_trade_profit_with_winning_trade()
        self.update_sum_of_profits()
        self.make_backtest_row = True

    def enter_entry(self):
        pass

    def enter_long(self):
        """ when the FSM enters long a long position is opened """
        self.update_market_enter_price()
        self.update_current_take_profit_long()
        self.update_current_stop_loss_long()
        self.update_trade_open_time()
        self.set_side("long")
        self.update_quantity()
        self.update_open_fees()

    def execute_long(self):
        """ as soon as the current price of the coin is bigger than take profit the fsm goes to entry
        if it is smaller than current stop loss the fsm goes to stop loss"""
        if self.current_price > self.current_take_profit:
            self.make_file_line()
            self.long_to_entry()
        if self.current_price < self.current_stop_loss:
            self.long_to_stop_loss()

    def exit_long(self):
        pass

    def enter_short(self):
        """ when the FSM enters short a short position is opened """
        self.update_market_enter_price()
        self.update_current_take_profit_short()
        self.update_current_stop_loss_short()
        self.update_trade_open_time()
        self.set_side("short")
        self.update_quantity()
        self.update_open_fees()

    def execute_short(self):
        """ as soon as the current price of the coin is smaller than take profit the fsm goes to entry
        if it is bigger than current stop loss, the fsm goes to stop loss"""
        if self.current_price < self.current_take_profit:
            self.make_file_line()
            self.short_to_entry()
        if self.current_price > self.current_stop_loss:
            self.short_to_stop_loss()

    def exit_short(self):
        pass

    def enter_stop_loss(self):
        """ when a trade is closed because a stop loss is trigger this state is entered """
        self.set_success("loss")
        self.increment_losses()
        self.update_market_exit_price()
        self.update_close_fees()
        self.update_trade_close_time()
        self.update_trade_profit_with_losing_trade()
        self.update_sum_of_profits()
        self.make_backtest_row = True

    @abstractmethod
    def execute_entry(self):
        """ Has to be implemented be all child classes which inheritance this parent class. Handles the logic
        when a position should be opened """
        raise NotImplementedError

    @abstractmethod
    def execute_stop_loss(self):
        """ Has to be implemented be all child classes which inheritance this parent class. Handles the logic what
        happens if a stop loss order was executed. """
        raise NotImplementedError

    def __str__(self):
        if self.fetching_market_data:
            return ("Fetching market data, coin:" + self.coin + ", dollar:" + str(self.dollar) +
                    ", trading fees:" + str(self.fees))
        elif not self.fetching_market_data and self.calculating:
            return ("Calculating, run: " + "1/1" + ", coin:" + self.coin +
                    ", dollar:" + str(self.dollar) + ", trading fees:" + str(self.fees))
        elif not self.calculating:
            return "Done, coin:" + self.coin + ", dollar:" + str(self.dollar) + ", trading fees:" + str(
                self.fees) + ", result:" + str(self.win)


class RsiBacktest(Backtest):
    """ Implements the RSI strategy backtest logic """
    def __init__(self, coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss, trading_fees,
                 days, overbought, oversold, single_backtest):
        super().__init__(coin, dollar, take_profit, stop_loss, name_of_file, days, trading_fees,
                         single_backtest, time_frame, length)
        # the price at which a coin is overbought
        self.overbought = overbought
        # the price at which a coin is oversold
        self.oversold = oversold
        # the current rsi of the coin
        self.rsi = None
        self.last_rsi = -1
        self.header_list = ["coin", "dollar", "time_frame", "length", "overbought", "oversold", "take profit",
                            "stop loss", "days", "current take profit", "current stop loss", "side", "open time",
                            "open price", "open fees", "quantity", "close time", "close price", "close fees",
                            "success", "winning trades", "losing trades", "trade profit", "profit"]

    def set_current_rsi(self, rsi):
        self.rsi = round(rsi, 2)

    def make_only_result_csv_file(self):
        self.single_trade = []
        super().append_trade_settings()
        self.single_trade.append(self.overbought)
        self.single_trade.append(self.oversold)
        super().append_single_trade_outcome()
        self.trades.append(self.single_trade)

    def make_row_for_csv_file_with_trade_data(self):
        self.update_money_per_trade()
        if self.single_backtest:
            self.single_trade = []
            super().append_trade_settings()
            self.single_trade.append(self.overbought)
            self.single_trade.append(self.oversold)
            super().append_trade_outcome()

    def execute_entry(self):
        """ gets the current rsi. when the rsi is smaller than the oversold value a long position is opened.
        Is the rsi is bigger than oversold a short position is opened"""
        if self.rsi < self.oversold:
            self.entry_to_long()
        if self.rsi > self.overbought:
            self.entry_to_short()

    def execute_stop_loss(self):
        """ when a stop loss was triggered the next candles are skipped until a "normal" rsi is reached"""
        middle = (self.overbought + self.oversold) / 2
        if self.last_rsi <= middle <= self.rsi or self.rsi >= middle >= self.last_rsi:
            self.stop_loss_to_entry()
        self.last_rsi = self.rsi


class MABacktest(Backtest):
    """ Implements the Ma strategy backtest logic """
    def __init__(self, coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss, trading_fees,
                 days, single_backtest):
        super().__init__(coin, dollar, take_profit, stop_loss, name_of_file, days, trading_fees, single_backtest,
                         time_frame, length)
        self.ma = None
        self.open = 0
        self.close = 0
        self.high = 0
        self.low = 0
        self.header_list = ["coin", "dollar", "time_frame", "length", "take profit",
                            "stop loss", "days", "current take profit", "current stop loss", "side", "open time",
                            "open price", "open fees", "quantity", "close time", "close price", "close fees",
                            "success", "winning trades", "losing trades", "trade profit", "profit"]

    def make_only_result_csv_file(self):
        self.single_trade = []
        super().append_trade_settings()
        super().append_single_trade_outcome()
        self.trades.append(self.single_trade)

    def make_row_for_csv_file_with_trade_data(self):
        self.update_money_per_trade()
        if self.single_backtest:
            self.single_trade = []
            super().append_trade_settings()
            super().append_trade_outcome()

    def execute_entry(self):
        """ when the current candle breaks through the ma from below a long position is opened. When it breaks
        through from above a short position is opened"""
        if float(self.low) < float(self.ma) < float(self.high):
            if float(self.open) < float(self.close):
                self.entry_to_long()
            else:
                self.entry_to_short()

    def execute_stop_loss(self):
        """ When a stop loss is triggerd nothing should happen the strategy just goes back to entry and waits for the
        next opportunity """
        self.stop_loss_to_entry()
