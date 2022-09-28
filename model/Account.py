from model.Coin import *
from model.MarketData import MarketData
from model.Fsm import Fsm
import datetime
import copy


class Account:
    """ saves all trading Strategies. And creates new Strategies """
    def __init__(self):
        self.manuel_strategy = []
        self.rsi_strategy = []
        self.rsi_backtest_strategy = []
        self.ma_strategy = []
        self.ma_backtest_strategy = []
        self.all_markets = []
        self.all_active_strategies = [self.manuel_strategy,
                                      self.rsi_strategy,
                                      self.rsi_backtest_strategy,
                                      self.ma_strategy,
                                      self.ma_backtest_strategy]
        # the time in which new market datas are fetched in seconds
        self.update_time = 10
        self.market_data = MarketData()

    def new_rsi_live(self, coin, dollar, order_type, min_order_size, account, take_profit, stop_loss,
                     overbought, oversold, time_frame, length):
        rsi = RsiLive(coin, dollar, order_type, min_order_size, account, take_profit, stop_loss,
                      overbought, oversold, time_frame, length)
        rsi.set_current_rsi(round(MarketData().get_last_rsi(coin, time_frame, length), 2))
        self.rsi_strategy.append(rsi)
        return rsi

    def new_rsi_backtest(self, coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss,
                         trading_fees, days, overbought, oversold, single_backtest):
        rsi = RsiBacktest(coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss,
                          trading_fees, days, overbought, oversold, single_backtest)
        if single_backtest:
            self.rsi_backtest_strategy.append(rsi)
        return rsi

    def new_ma_live(self, coin, dollar, order_type, min_order_size, account, take_profit, stop_loss,
                    time_frame, length):
        ma = MALive(coin, dollar, order_type, min_order_size, account, take_profit, stop_loss,
                    time_frame, length)
        ma.set_current_ma(round(MarketData().get_current_ma(coin, time_frame, length), 2))
        self.ma_strategy.append(ma)
        return ma

    def new_ma_backtest(self, coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss,
                        trading_fees, days, single_backtest):
        ma = MABacktest(coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss,
                        trading_fees, days, single_backtest)
        if single_backtest:
            self.ma_backtest_strategy.append(ma)
        return ma

    def new_manuel_trading(self, coin, dollar, order_type, min_order_size, account):
        strategy = ManuelTrading(coin, float(dollar), order_type, min_order_size, account)
        self.manuel_strategy.append(strategy)
        return strategy

    def get_all_active_strategies(self):
        return self.all_active_strategies

    def extend_all_active_strategies(self, strategies):
        """ extends the list all_active_strategies"""
        for index, item in enumerate(strategies):
            self.all_active_strategies[index].extend(strategies[index])

    def get_rsi_strategy(self):
        return self.rsi_strategy

    def set_rsi_strategy(self, rsi):
        self.rsi_strategy = rsi

    def get_market_data(self):
        return self.market_data

    def get_ma_strategy(self):
        return self.ma_strategy

    def get_active_manuel_strategies(self):
        return self.manuel_strategy

    def get_manuel_strategy(self, coin):
        for strategy in self.manuel_strategy:
            if strategy.coin == coin:
                return strategy
        return None

    def get_all_markets(self):
        return self.all_markets

    def delete_manuel_strategy(self, strategy):
        self.manuel_strategy.remove(strategy)

    def delete_manuel_strategy_index(self, index):
        return self.manuel_strategy.pop(index)

    @staticmethod
    def bind_fsm(strategy):
        Fsm(strategy)

    def set_all_markets(self):
        markets_copy = copy.deepcopy(self.all_markets)
        """ fetches all markets and keeps all PERP markets and saves them in all_markets """
        try:
            markets = self.market_data.get_markets()
        except Exception as e:
            print("error in set all markets")
            now = datetime.datetime.now()
            print(now)
            print(e)
            self.all_markets = markets_copy
            self.market_data = MarketData()
        else:
            self.set_the_markets(markets)

    def set_the_markets(self, markets):
        markets_new = []
        for m in markets:
            if "PERP" in m['name']:
                markets_new.append(m)
        self.all_markets = markets_new

    def get_min_order_size(self, coin):
        for m in self.all_markets:
            if coin in m['name']:
                return m['minProvideSize']

    @staticmethod
    def get_balance(values):
        """ returns account information """
        account = BuySell("BTC", values)
        account_info = account.get_account_info()
        return account_info

    def get_coin_list(self):
        """ returns a list with the coins of all available coins """
        all_coins = []
        for market in self.get_all_markets():
            name = market['name']
            name_without_perp = name.replace("-PERP", "")
            all_coins.append(name_without_perp)
        return all_coins

    def get_rsi_backtest_strategy(self):
        return self.rsi_backtest_strategy

    def get_ma_backtest_strategy(self):
        return self.ma_backtest_strategy

    def delete_all_rsi_backtest_strategy(self):
        self.rsi_backtest_strategy.clear()

    def delete_all_ma_backtest_strategy(self):
        self.ma_backtest_strategy.clear()
