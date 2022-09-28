import time
from threading import *
from concurrent.futures import ThreadPoolExecutor
import datetime
import copy


class UpdateController:
    """ Updates all Strategies and collateral in account.update.time second intervals. When updating a strategy it
    executes its Fsm so that the strategy can do whatever is coded in his strategy when other market conditions are
    meet"""

    def __init__(self):
        self.account = None
        self.login_controller = None
        self.frames = None

    def set_account(self, account):
        self.account = account

    def set_frames(self, frames):
        self.frames = frames

    def set_login_controller(self, login_controller):
        self.login_controller = login_controller

    def update_time(self, time_in_sec):
        self.account.update_time = time_in_sec

    def get_balance(self, frame, account_name):
        """ gets account info's of the account with name account_name and sets free and available collateral in GUI """
        values = self.login_controller.get_values(account_name)
        balance = self.account.get_balance(values)
        frame.set_balance(balance)

    def give_balance(self, account_name):
        """ gets account info's of the account with name account_name and returns them """
        values = self.login_controller.get_values(account_name)
        return self.account.get_balance(values)

    def update(self):
        """ updates everything """
        def update_price():
            while True:
                self.account.set_all_markets()
                update_manual_strategies()
                execute_rsi_strategies()
                execute_ma_strategies()
                update_gui_balances()
                time.sleep(self.account.update_time)

        def update_gui_balances():
            frames = [self.frames['ManuelTrading'], self.frames['RSITrading'], self.frames['MaTrading']]
            accounts = selected_gui_values()
            if accounts:
                for account in accounts:
                    try:
                        balance = self.give_balance(account)
                        for frame in frames:
                            if frame.select_account.get() == account:
                                frame.set_balance(balance)
                    except Exception as e:
                        print(e)

        def selected_gui_values():
            """ return the values of the selected accounts in all GUI frames which have those"""
            values = []
            if self.frames['ManuelTrading'].select_account.get():
                values.append(self.frames['ManuelTrading'].select_account.get())
            if self.frames['RSITrading'].select_account.get():
                values.append(self.frames['RSITrading'].select_account.get())
            if self.frames['MaTrading'].select_account.get():
                values.append(self.frames['MaTrading'].select_account.get())
            while "Select an Option" in values:
                values.remove("Select an Option")
            return values

        def execute_rsi_strategies():
            """ executes all RSI strategies and sets the GUI to the new values """
            rsi_strategies = self.account.get_rsi_strategy()
            set_rsi_of_strategies()
            for strategy in rsi_strategies:
                strategy.set_current_price(get_price(self.account.get_all_markets(), strategy.coin))
                self.frames['RSITrading'].update_list_box()
                self.execute(strategy)
                self.frames['RSITrading'].update_list_box()

        def execute_ma_strategies():
            """ executes all MA ma_strategies and sets the GUI to the new values """
            ma_strategies = self.account.get_ma_strategy()
            set_ma_of_rsi_strategies()
            for strategy in ma_strategies:
                strategy.last_price = strategy.current_price
                strategy.set_current_price(get_price(self.account.get_all_markets(), strategy.coin))
                self.frames['MaTrading'].update_list_box()
                self.execute(strategy)
                self.frames['MaTrading'].update_list_box()

        def update_manual_strategies():
            manuel_ma_rsi_strategies = self.account.get_active_manuel_strategies()
            for strategy in manuel_ma_rsi_strategies:
                strategy.set_current_price(get_price(self.account.get_all_markets(), strategy.coin))
                self.frames['ManuelTrading'].update_list_box()

        def get_price(markets, coin):
            """ returns the price of the coin  """
            for c in markets:
                if c['name'] == coin + "-PERP":
                    return c['price']

        def set_ma_of_rsi_strategies():
            """ sets ma of all active ma ma_rsi_strategies """
            ma_rsi_strategy = self.account.get_ma_strategy()
            with ThreadPoolExecutor(max_workers=20) as executor:
                for strategy in ma_rsi_strategy:
                    executor.submit(set_ma, strategy)

        def set_ma(strategy):
            if strategy.ma is not None:
                ma_copy = strategy.ma
            else:
                ma_copy = 0
            try:
                strategy.set_current_ma(self.account.market_data.get_current_ma(strategy.coin, strategy.time_frame,
                                                                                strategy.length))
                self.frames['MaTrading'].update_list_box()
            except Exception as e:
                now = datetime.datetime.now()
                print("error in set ma")
                print(now)
                print(e)
                strategy.ma = ma_copy

        def set_rsi_of_strategies():
            """ sets rsi of all rsi rsi_strategies. Orders the rsi_strategies by their coin time_frame and length.
            Then only one api call with the rsi_strategy with the biggest length is executed. The RSIs of the
            rsi_strategies with smaller length and same coin and time_Frame can be calculated with the longer
            length as well"""
            rsi_strategies = self.account.get_rsi_strategy()
            rsi_strategies_copy = copy.deepcopy(rsi_strategies)
            rsi_strategies.sort(key=lambda x: (x.coin, x.time_frame, int(x.length)), reverse=True)
            coin = "no_coin"
            time_frame = "no_frame"
            candle_list = None
            try:
                for strategy in rsi_strategies:
                    if strategy.coin != coin or strategy.time_frame != time_frame:
                        coin = strategy.coin
                        time_frame = strategy.time_frame
                        candle_list = self.account.market_data.get_candle_list(strategy.coin + "-PERP",
                                                                               strategy.time_frame,
                                                                               int(strategy.length))
                    strategy.set_current_rsi(self.account.market_data.get_last_rsi_of_list(candle_list,
                                                                                           strategy.length))
                    self.frames['RSITrading'].update_list_box()
            except Exception as e:
                now = datetime.datetime.now()
                print("error in set rsi of strategies")
                print(now)
                print(e)
                self.account.set_rsi_strategy(rsi_strategies_copy)

        t1 = Thread(target=update_price)
        t1.daemon = True
        t1.start()

    @staticmethod
    def execute(strategy):
        """ Transitions from State to the same State. Transition logic to other
        States is done in the TradeParameters class"""
        state = strategy.state
        if state == "entry":
            strategy.execute_entry()
        elif state == "long":
            strategy.execute_long()
        elif state == "short":
            strategy.execute_short()
        elif state == "stop_loss":
            strategy.execute_stop_loss()
        elif state == "done":
            strategy.execute_done()
