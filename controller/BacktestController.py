import pandas as pd
from threading import *


class BacktestController:
    """ Handles the Backtest logic. Checks user inputs and makes the Tests"""
    def __init__(self):
        self.account = None
        self.user_input_controller = None
        self.market_data = None
        self.historical_prices_controller = None
        """ if the user presses stop Backtest self.stop is set to True. At the next
        possible moment the Backtest will be stopped. In this case no Backtest
        file is created"""
        self.stop = False

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
        # whenever a trade cycle is done the strategy sets make_backtest_row to True.
        # All values out of this cycle are written to a new csv line then
        if strategy.make_backtest_row:
            strategy.make_row_for_csv_file_with_trade_data()
            strategy.make_backtest_row = False

    def bind_fsm(self, strategy):
        """binds the FSM to this strategy"""
        self.account.bind_fsm(strategy)

    def set_account(self, account):
        self.account = account
        self.market_data = account.get_market_data()

    def set_user_input_controller(self, user_input_controller):
        self.user_input_controller = user_input_controller

    def set_historical_prices_controller(self, historical_prices_controller):
        self.historical_prices_controller = historical_prices_controller

    def delete_file(self, name_of_file):
        self.historical_prices_controller.delete_file(name_of_file)

    def load_prices(self, coin, time_frame):
        """ Gets all coins with the  matching time frame from the API """
        self.historical_prices_controller.write_data(coin, time_frame)

    def load_all_prices(self, frame, coins, time_frames):
        """ iterates over all coins and timeframes which the user passed over and loads
         all candles from this coin """
        for c in coins:
            for t in time_frames:
                frame.show_current_run("fetching market data: " + c + " " + t)
                if self.stop:
                    frame.show_current_run("calculation canceled")
                    self.stop = False
                    return
                self.load_prices(c, t)

    def get_historical_prices(self, coin, time_frame, days):
        """ loads the candle data of past market data out of a csv file """
        return self.historical_prices_controller.read_data(coin, time_frame, int(days))

    def execute_strategy(self, frame, strategy, single_strategy, data, rsi, is_ma_strategy):
        counter = int(strategy.length)
        """ every time execute is called the FSM bound to this strategy will make a
        Transition. The Transition is from this specific State to this exact State.
        Transitions to other State are done in the TradeParameters Class logic """
        while True:
            if counter >= len(data):
                if single_strategy:
                    self.historical_prices_controller.make_backtest_file(strategy)
                    strategy.calculating = False
                    frame.update_list_box()
                break
            # sets current price to the middle of high and low of the current candle
            strategy.current_price = float(data[counter][5])
            strategy.current_time = data[counter][0]
            if is_ma_strategy:
                strategy.ma = (rsi[counter])
                strategy.open = float(data[counter][2])
                strategy.close = float(data[counter][5])
                strategy.high = float(data[counter][3])
                strategy.low = float(data[counter][4])
            else:
                strategy.rsi = (rsi[counter])
            counter += 1
            self.execute(strategy)

    def get_list_of_coins(self, coin):
        return self.user_input_controller.get_list(coin)

    def get_list_of_interval(self, lower, upper, interval):
        return self.user_input_controller.get_value_list(lower, upper, interval)

    @staticmethod
    def get_round_size(number):
        number = int(str(number)[::-1].find('.'))
        if number == -1:
            return 1
        else:
            return number

    def order_file(self, frame, header_list, name_of_file, data):
        frame.show_current_run("order file")
        self.historical_prices_controller.order_backtest_file(name_of_file, header_list, data)
        frame.show_current_run("Done")

    def standard_parameters_are_ok(self, frame, coin, dollar, time_frame, length, name_of_file, take_profit, stop_loss,
                                   trading_fees, days):
        """ checks user inputs of parameters which the user has to pass regardless of the strategy """
        if not self.user_input_controller.coin_exists(frame, coin):
            return False
        ints = {'length': length, 'days': days}
        if not self.user_input_controller.is_a_int(frame, ints):
            return False
        if not self.user_input_controller.file_name_exists(frame, name_of_file):
            return False
        if not self.user_input_controller.time_frame_exists(frame, time_frame):
            return False
        values = {'dollar': dollar, 'take profit': take_profit,
                  'stop loss': stop_loss, 'trading fees': trading_fees}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        floats = {'dollar': dollar, 'take profit': take_profit, 'stop loss': stop_loss, 'trading fees': trading_fees}
        if not self.user_input_controller.is_positive(frame, floats):
            return False
        return True

    def standard_interval_parameters_are_ok(self, frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                            take_profit_lower, take_profit_upper, take_profit_interval,
                                            stop_loss_lower, stop_loss_upper, stop_loss_interval,
                                            days_to_backtest_lower, days_to_backtest_upper, days_to_backtest_interval,
                                            length_lower, length_upper, length_interval):
        """ checks user inputs of interval parameters which the user has to pass regardless of the strategy """
        ints = {'length lower': length_lower,
                'length upper': length_upper,
                'length interval': length_interval,
                'days to backtest_lower': days_to_backtest_lower,
                'days to backtest_upper': days_to_backtest_upper,
                'days to backtest_interval': days_to_backtest_interval}
        if not self.user_input_controller.coins_exists(frame, coin):
            return False
        if not self.user_input_controller.is_a_int(frame, ints):
            return False
        if not self.user_input_controller.file_name_exists(frame, name_of_file):
            return False
        if not self.user_input_controller.time_frames_exists(frame, time_frame):
            return False
        if not self.user_input_controller.trading_fees_are_ok(frame, trading_fees):
            return False
        values = {'dollar': dollar,
                  'take profit lower': take_profit_lower,
                  'take profit upper': take_profit_upper,
                  'take profit interval': take_profit_interval,
                  'stop loss lower': stop_loss_lower,
                  'stop loss upper': stop_loss_upper,
                  'stop loss interval': stop_loss_interval}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        interval = {'take profit lower': [take_profit_lower, 0.01, 10000],
                    'take profit upper': [take_profit_upper, 0.01, 10000],
                    'take profit interval': [take_profit_interval, 0.01, 10000],
                    'stop loss lower': [stop_loss_lower, 0.01, 10000],
                    'stop loss upper': [stop_loss_upper, 0.01, 10000],
                    'stop loss interval': [stop_loss_interval, 0.01, 10000],
                    'days to backtest lower': [days_to_backtest_lower, 1, 365],
                    'days to backtest upper': [days_to_backtest_upper, 1, 365],
                    'days to backtest interval': [days_to_backtest_interval, 1, 365]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False

        interval = {'take profit interval': [take_profit_lower, take_profit_upper, take_profit_interval],
                    'stop loss interval': [stop_loss_lower, stop_loss_upper, stop_loss_interval],
                    'days to backtest interval': [days_to_backtest_lower, days_to_backtest_upper,
                                                  days_to_backtest_interval],
                    'length interval': [length_lower, length_upper, length_interval]}
        if not self.user_input_controller.is_interval(frame, interval):
            return False
        floats = {'dollar': dollar,
                  'days to backtest interval': days_to_backtest_interval,
                  'length interval': length_interval}
        if not self.user_input_controller.is_positive(frame, floats):
            return False
        smaller = [[take_profit_lower, take_profit_upper, "take_profit_lower", "take_profit_upper"],
                   [stop_loss_lower, stop_loss_upper, "stop_loss_lower", "stop_loss_upper"],
                   [days_to_backtest_lower, days_to_backtest_upper, "days_to_backtest_lower", "days_to_backtest_upper"],
                   [length_lower, length_upper, "length_lower", "length_upper"]]
        if not self.user_input_controller.is_smaller(frame, smaller):
            return False
        return True


class RSIControllerBacktrack(BacktestController):
    """ Handles the RSI Backtest logic. Checks user inputs and makes the Tests """
    def __init__(self):
        super().__init__()

    def get_all_rsi_backtest_strategies(self):
        return self.account.get_rsi_backtest_strategy()

    def delete_strategy(self, frame, index):
        self.account.get_rsi_backtest_strategy().pop(index)
        frame.update_list_box()

    def delete_all_strategies(self, frame):
        self.account.delete_all_rsi_backtest_strategy()
        frame.update_list_box()

    def single_parameters_are_ok(self, frame, coin, dollar, time_frame, length, name_of_file, overbought, oversold,
                                 take_profit, stop_loss, trading_fees, days):
        """ checks user inputs of parameters which only exist at this specific Strategy (RSI) """
        if not self.standard_parameters_are_ok(frame, coin, dollar, time_frame, length, name_of_file,
                                               take_profit, stop_loss, trading_fees, days):
            return False
        values = {'overbought': overbought, 'oversold': oversold}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        interval = {'length': [length, 1, 50], 'days': [days, 1, 365]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False
        interval = {'overbought': [overbought, 0, 100], 'oversold': [oversold, 0, 100]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False
        smaller = [[oversold, overbought, "oversold", "overbought"]]
        if not self.user_input_controller.is_smaller(frame, smaller):
            return False
        frame.show_error_massage("")
        return True

    @staticmethod
    def get_close(data):
        """ keeps only the close prices of all candles in data """
        close = []
        for d in data:
            close.append(float(d[5]))
        return close

    def get_rsi(self, close, length):
        """ calculates all rsi for all candles in close. The RSI of the first length candles will be NaN """
        closes = self.get_close(close)
        m = self.market_data
        data_frame = {"close": closes}
        df = pd.DataFrame(data_frame)
        rsi = m.get_rsi_list(df, int(length))
        return rsi

    def start_single_backtest(self, frame, coin, dollar, time_frame, length, name_of_file, overbought, oversold,
                              take_profit, stop_loss, trading_fees, days):
        if self.single_parameters_are_ok(frame, coin, dollar, time_frame, length, name_of_file, overbought, oversold,
                                         take_profit, stop_loss, trading_fees, days):
            self.delete_file(name_of_file)

            def execute_backtest_strategies():
                rsi_strategy = self.account.new_rsi_backtest(coin, float(dollar), time_frame, float(length),
                                                             name_of_file, float(take_profit), float(stop_loss),
                                                             float(trading_fees), int(days), float(overbought),
                                                             float(oversold), True)
                frame.update_list_box()
                self.load_prices(coin, time_frame)
                data = self.get_historical_prices(coin, time_frame, days)
                rsi = self.get_rsi(data, length)
                rsi_strategy.fetching_market_data = False
                # binds the FSM to the strategy
                self.bind_fsm(rsi_strategy)
                frame.update_list_box()
                self.execute_strategy(frame, rsi_strategy, True, data, rsi, False)

            t1 = Thread(target=execute_backtest_strategies)
            t1.daemon = True
            t1.start()

    def interval_parameters_are_ok(self, frame, dollar, name_of_file, coin, time_frame, trading_fees, overbought_lower,
                                   overbought_upper, overbought_interval, oversold_lower, oversold_upper,
                                   oversold_interval, take_profit_lower, take_profit_upper, take_profit_interval,
                                   stop_loss_lower, stop_loss_upper, stop_loss_interval, days_to_backtest_lower,
                                   days_to_backtest_upper, days_to_backtest_interval, length_lower, length_upper,
                                   length_interval):
        if not self.standard_interval_parameters_are_ok(frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                                        take_profit_lower, take_profit_upper, take_profit_interval,
                                                        stop_loss_lower, stop_loss_upper, stop_loss_interval,
                                                        days_to_backtest_lower, days_to_backtest_upper,
                                                        days_to_backtest_interval, length_lower, length_upper,
                                                        length_interval):
            return False
        values = {'overbought lower': overbought_lower,
                  'overbought upper': overbought_upper,
                  'overbought interval': overbought_interval,
                  'oversold lower': oversold_lower,
                  'oversold upper': oversold_upper,
                  'oversold interval': oversold_interval}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        interval = {'overbought lower': [overbought_lower, 0, 100],
                    'overbought upper': [overbought_upper, 0, 100],
                    'overbought interval': [overbought_interval, 0.01, 100],
                    'oversold lower': [overbought_lower, 0, 100],
                    'oversold upper': [overbought_upper, 0, 100],
                    'oversold interval': [overbought_interval, 0.01, 100],
                    'length lower': [length_lower, 1, 50],
                    'length upper': [length_upper, 1, 50],
                    'length interval': [length_interval, 1, 50]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False
        smaller = [[take_profit_lower, take_profit_upper, "take profit lower", "take profit upper"],
                   [stop_loss_lower, stop_loss_upper, "stop loss lower", "stop loss upper"],
                   [days_to_backtest_lower, days_to_backtest_upper, "days to backtest lower", "days to backtest upper"],
                   [length_lower, length_upper, "length lower", "length upper"]]
        if not self.user_input_controller.is_smaller(frame, smaller):
            return False

        frame.show_error_massage("")
        return True

    def start_multiple_backtest(self, frame, dollar, name_of_file, coin, time_frame, trading_fees, overbought_lower,
                                overbought_upper, overbought_interval, oversold_lower, oversold_upper,
                                oversold_interval, take_profit_lower, take_profit_upper, take_profit_interval,
                                stop_loss_lower, stop_loss_upper, stop_loss_interval, days_to_backtest_lower,
                                days_to_backtest_upper, days_to_backtest_interval, length_lower, length_upper,
                                length_interval):
        if self.interval_parameters_are_ok(frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                           overbought_lower, overbought_upper, overbought_interval,
                                           oversold_lower, oversold_upper, oversold_interval,
                                           take_profit_lower, take_profit_upper, take_profit_interval,
                                           stop_loss_lower, stop_loss_upper, stop_loss_interval,
                                           days_to_backtest_lower, days_to_backtest_upper, days_to_backtest_interval,
                                           length_lower, length_upper, length_interval):

            def execute_backtest_strategies():
                coins = self.get_list_of_coins(coin)
                time_frames = self.get_list_of_coins(time_frame)
                trading_fees_values = self.get_list_of_coins(trading_fees)
                overbought_values = self.get_list_of_interval(overbought_lower, overbought_upper, overbought_interval)
                oversold_values = self.get_list_of_interval(oversold_lower, oversold_upper, oversold_interval)
                take_profit_values = self.get_list_of_interval(take_profit_lower, take_profit_upper,
                                                               take_profit_interval)
                stop_loss_values = self.get_list_of_interval(stop_loss_lower, stop_loss_upper, stop_loss_interval)
                day_values = self.get_list_of_interval(days_to_backtest_lower, days_to_backtest_upper,
                                                       days_to_backtest_interval)
                length_values = self.get_list_of_interval(length_lower, length_upper, length_interval)
                self.delete_file(name_of_file)
                self.load_all_prices(frame, coins, time_frames)

                runs = (len(coins) * len(time_frames) * len(trading_fees_values) * len(overbought_values) *
                        len(oversold_values) * len(take_profit_values) * len(stop_loss_values) * len(day_values) *
                        len(length_values))

                results = []
                counter = 0
                for t in time_frames:
                    for c in coins:
                        for length in length_values:
                            for day in day_values:
                                data = self.get_historical_prices(c, t, day)
                                rsi = self.get_rsi(data, length)
                                for trading_fee in trading_fees_values:
                                    for overbought_value in overbought_values:
                                        for oversold_value in oversold_values:
                                            for take_profit_value in take_profit_values:
                                                for stop_loss_value in stop_loss_values:
                                                    string = self.get_string(counter, runs, t, c, length, day,
                                                                             overbought_value, overbought_interval,
                                                                             oversold_value, oversold_interval,
                                                                             take_profit_value, take_profit_interval,
                                                                             stop_loss_value, stop_loss_interval)

                                                    frame.show_current_run(string)
                                                    counter += 1
                                                    self.calculate(frame, results, c, dollar, t, length, name_of_file,
                                                                   take_profit_value, stop_loss_value, trading_fee,
                                                                   day, overbought_value, oversold_value, rsi, data)
                                                    if self.stop:
                                                        frame.show_current_run("calculation canceled")
                                                        self.stop = False
                                                        return
                header_list = ["coin", "dollar", "time frame", "length", "overbought", "oversold", "take profit",
                               "stop loss", "days", "number of winning trades", "number of losing trades", "profit"]
                self.order_file(frame, header_list, name_of_file, results)

            t2 = Thread(target=execute_backtest_strategies)
            t2.daemon = True
            t2.start()

    def get_string(self, counter, runs, t, c, length, day, overbought_value, overbought_interval, oversold_value,
                   oversold_interval, take_profit_value, take_profit_interval, stop_loss_value, stop_loss_interval):
        round_take_profit = round(take_profit_value, self.get_round_size(take_profit_interval))
        round_stop_loss = round(stop_loss_value, self.get_round_size(stop_loss_interval))
        round_overbought_value = round(overbought_value, self.get_round_size(overbought_interval))
        round_oversold_value = round(oversold_value, self.get_round_size(oversold_interval))
        return ("calculating run: " + str(counter) + "/" + str(runs) +
                "\n"
                "\n" + "time: " + str(t) +
                "\n" + "coin: " + str(c) +
                "\n" + "length: " + str(int(length)) +
                "\n" + "days: " + str(int(day)) +
                "\n" + "overbought: " + str(round_overbought_value) +
                "\n" + "oversold: " + str(round_oversold_value) +
                "\n" + "take profit " + str(round_take_profit) +
                "\n" + "stop loss: " + str(round_stop_loss))

    def calculate(self, frame, results,  c, dollar, t, length, name_of_file, take_profit_value, stop_loss_value,
                  trading_fee, day, overbought_value, oversold_value, rsi, data):
        rsi_strategy = self.account.new_rsi_backtest(c, float(dollar), t, float(length), name_of_file,
                                                     float(take_profit_value), float(stop_loss_value),
                                                     float(trading_fee), int(day), float(overbought_value),
                                                     float(oversold_value), False)

        self.bind_fsm(rsi_strategy)
        self.execute_strategy(frame, rsi_strategy, False, data, rsi, False)
        rsi_strategy.make_only_result_csv_file()
        results.append(rsi_strategy.trades[0])


class MAControllerBacktrack(BacktestController):
    def __init__(self):
        super().__init__()

    def get_all_ma_backtest_strategies(self):
        return self.account.ma_backtest_strategy

    def delete_strategy(self, frame, index):
        self.account.get_ma_backtest_strategy().pop(index)
        frame.update_list_box()

    def delete_all_strategies(self, frame):
        self.account.delete_all_ma_backtest_strategy()
        frame.update_list_box()

    def single_parameters_are_ok(self, frame, coin, dollar, time_frame, length, name_of_file,
                                 take_profit, stop_loss, trading_fees, days):
        if not self.standard_parameters_are_ok(frame, coin, dollar, time_frame, length, name_of_file,
                                               take_profit, stop_loss, trading_fees, days):
            return False
        interval = {'length': [length, 1, 1000], 'days': [days, 1, 365]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False
        frame.show_error_massage("")
        return True

    def start_single_backtest(self, frame, coin, dollar, time_frame, length, name_of_file,
                              take_profit, stop_loss, trading_fees, days):
        if self.single_parameters_are_ok(frame, coin, dollar, time_frame, length, name_of_file,
                                         take_profit, stop_loss, trading_fees, days):
            self.delete_file(name_of_file)

            def execute_backtest_strategy():
                ma_strategy = self.account.new_ma_backtest(coin, float(dollar), time_frame, float(length),
                                                           name_of_file, float(take_profit), float(stop_loss),
                                                           float(trading_fees), int(days), True)
                frame.update_list_box()
                self.load_prices(coin, time_frame)
                data = self.get_historical_prices(coin, time_frame, days)
                ma_strategy.fetching_market_data = False
                # binds the FSM to the strategy
                self.bind_fsm(ma_strategy)
                frame.update_list_box()
                self.execute_strategy(frame, ma_strategy, True, data, self.market_data.get_all_mas(data, int(length)),
                                      True)

            t1 = Thread(target=execute_backtest_strategy)
            t1.daemon = True
            t1.start()

    def interval_parameters_are_ok(self, frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                   take_profit_lower, take_profit_upper, take_profit_interval,
                                   stop_loss_lower, stop_loss_upper, stop_loss_interval, days_to_backtest_lower,
                                   days_to_backtest_upper, days_to_backtest_interval, length_lower, length_upper,
                                   length_interval):
        if not self.standard_interval_parameters_are_ok(frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                                        take_profit_lower, take_profit_upper, take_profit_interval,
                                                        stop_loss_lower, stop_loss_upper, stop_loss_interval,
                                                        days_to_backtest_lower, days_to_backtest_upper,
                                                        days_to_backtest_interval,
                                                        length_lower, length_upper, length_interval):
            return False
        interval = {'length lower': [length_lower, 1, 1000],
                    'length upper': [length_lower, 1, 1000],
                    'length interval': [length_interval, 1, 1000]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False

        frame.show_error_massage("")
        return True

    def start_multiple_backtest(self, frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                take_profit_lower, take_profit_upper, take_profit_interval,
                                stop_loss_lower, stop_loss_upper, stop_loss_interval, days_to_backtest_lower,
                                days_to_backtest_upper, days_to_backtest_interval, length_lower, length_upper,
                                length_interval):
        if self.interval_parameters_are_ok(frame, dollar, name_of_file, coin, time_frame, trading_fees,
                                           take_profit_lower, take_profit_upper, take_profit_interval,
                                           stop_loss_lower, stop_loss_upper, stop_loss_interval,
                                           days_to_backtest_lower, days_to_backtest_upper, days_to_backtest_interval,
                                           length_lower, length_upper, length_interval):

            def execute_backtest_strategies():
                coins = self.get_list_of_coins(coin)
                time_frames = self.get_list_of_coins(time_frame)
                trading_fees_values = self.get_list_of_coins(trading_fees)
                take_profit_values = self.get_list_of_interval(take_profit_lower, take_profit_upper,
                                                               take_profit_interval)
                stop_loss_values = self.get_list_of_interval(stop_loss_lower, stop_loss_upper, stop_loss_interval)
                day_values = self.get_list_of_interval(days_to_backtest_lower, days_to_backtest_upper,
                                                       days_to_backtest_interval)
                length_values = self.get_list_of_interval(length_lower, length_upper, length_interval)
                self.delete_file(name_of_file)
                self.load_all_prices(frame, coins, time_frames)

                runs = (len(coins) * len(time_frames) * len(trading_fees_values) *
                        len(take_profit_values) * len(stop_loss_values) * len(day_values) *
                        len(length_values))

                counter = 0
                results = []
                for t in time_frames:
                    for c in coins:
                        for length in length_values:
                            for day in day_values:
                                data = self.get_historical_prices(c, t, day)
                                ma = self.market_data.get_all_mas(data, int(length))
                                for trading_fee in trading_fees_values:
                                    for take_profit_value in take_profit_values:
                                        for stop_loss_value in stop_loss_values:
                                            string = self.get_string(counter, runs, t, c, length, day, trading_fee,
                                                                     take_profit_value, take_profit_interval,
                                                                     stop_loss_value, stop_loss_interval)

                                            frame.show_current_run(string)
                                            counter += 1
                                            self.calculate(frame, results, c, dollar, t, length, name_of_file,
                                                           take_profit_value, stop_loss_value, trading_fee,
                                                           day, ma, data)
                                            if self.stop:
                                                frame.show_current_run("calculation canceled")
                                                self.stop = False
                                                return
                header_list = ["coin", "dollar", "time frame", "length", "take profit",
                               "stop loss", "days", "number of winning trades", "number of losing trades", "profit"]
                self.order_file(frame, header_list, name_of_file, results)

            t2 = Thread(target=execute_backtest_strategies)
            t2.daemon = True
            t2.start()

    def get_string(self, counter, runs, t, c, length, day, trading_fee, take_profit_value, take_profit_interval,
                   stop_loss_value, stop_loss_interval):
        round_take_profit = round(take_profit_value, self.get_round_size(take_profit_interval))
        round_stop_loss = round(stop_loss_value, self.get_round_size(stop_loss_interval))
        return ("calculating run: " + str(counter) + "/" + str(runs) +
                "\n"
                "\n" + "time: " + str(t) +
                "\n" + "coin: " + str(c) +
                "\n" + "length: " + str(int(length)) +
                "\n" + "days: " + str(int(day)) +
                "\n" + "trading fee: " + str(trading_fee) +
                "\n" + "take profit " + str(round_take_profit) +
                "\n" + "stop loss: " + str(round_stop_loss))

    def calculate(self, frame, results, c, dollar, t, length, name_of_file, take_profit_value, stop_loss_value,
                  trading_fee, day, ma, data):
        ma_strategy = self.account.new_ma_backtest(c, float(dollar), t, float(length), name_of_file,
                                                   float(take_profit_value), float(stop_loss_value),
                                                   float(trading_fee), int(day), False)

        self.bind_fsm(ma_strategy)
        self.execute_strategy(frame, ma_strategy, False, data, ma, True)
        ma_strategy.make_only_result_csv_file()
        results.append(ma_strategy.trades[0])
