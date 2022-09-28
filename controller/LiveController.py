class LifeController:
    """Checks all standard user inputs and closes finite state machines"""
    def __init__(self):
        self.account = None
        self.user_input_controller = None
        self.login_controller = None

    def set_account(self, account):
        self.account = account

    def set_user_input_controller(self, user_input_controller):
        self.user_input_controller = user_input_controller

    def set_login_controller(self, login_controller):
        self.login_controller = login_controller

    """when the user presses stop trading bot the bot has to go in the final state done. It does this because if there 
    is a open long or short position they have to be closed first. When leaving long and short state this is done 
    automatically"""
    @staticmethod
    def execute(strategy):
        state = strategy.state
        if state == "entry":
            strategy.entry_to_done()
        elif state == "long":
            strategy.long_to_done()
        elif state == "short":
            strategy.short_to_done()
        elif state == "stop_loss":
            strategy.stop_loss_to_done()
        elif state == "done":
            strategy.execute_done()

    def standard_parameters_are_ok(self, frame, coin, dollar, order_type, account, take_profit, stop_loss, time_frame,
                                   length, collateral):
        if not account:
            frame.show_error_massage("Please add an Account")
            return False
        if not self.user_input_controller.coin_exists(frame, coin):
            return False
        ints = {'length': length}
        if not self.user_input_controller.is_a_int(frame, ints):
            return False
        selected = {'order_type': order_type, 'account': account, 'time_frame': time_frame}
        if not self.user_input_controller.values_are_selected(frame, selected):
            return False
        values = {'dollar': dollar, 'take_profit': take_profit,
                  'stop_loss': stop_loss}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        floats = {'dollar': dollar, 'take_profit': take_profit, 'stop_loss': stop_loss}
        if not self.user_input_controller.is_positive(frame, floats):
            return False
        if not self.user_input_controller.order_size_is_big_enough(frame, coin, dollar):
            return False
        if not self.user_input_controller.enough_collateral(frame, dollar, collateral):
            return False
        return True

    def bind_fsm(self, frame, strategy):
        """binds the FSM to this strategy and shows its settings in GUI """
        self.account.bind_fsm(strategy)
        frame.update_list_box()


class RSIController(LifeController):
    """Starts and Stops RSI strategies"""
    def __init__(self):
        super().__init__()

    def get_all_names(self):
        return self.account.get_rsi_strategy()

    def delete_strategy(self, frame, index):
        strategy = self.account.get_rsi_strategy().pop(index)
        self.execute(strategy)
        frame.update_list_box()

    def parameters_are_ok(self, frame, coin, dollar, order_type, account, take_profit, stop_loss, overbought,
                          oversold, time_frame, length, collateral):
        if not self.standard_parameters_are_ok(frame, coin, dollar, order_type, account, take_profit, stop_loss,
                                               time_frame, length, collateral):
            return False
        values = {'overbought': overbought, 'oversold': oversold}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        interval = {'length': [length, 1, 50]}
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

    def add_rsi_strategy(self, frame, coin, dollar, order_type, account, take_profit, stop_loss, overbought, oversold,
                         time_frame, length, collateral):
        min_order_size = self.account.get_min_order_size(coin)
        if self.parameters_are_ok(frame, coin, dollar, order_type, account, take_profit, stop_loss, overbought,
                                  oversold, time_frame, length, collateral):
            values = self.login_controller.get_values(account)
            rsi_strategy = self.account.new_rsi_live(coin, float(dollar), order_type, float(min_order_size),
                                                     values, float(take_profit), float(stop_loss),
                                                     float(overbought), float(oversold), time_frame, float(length))
            self.bind_fsm(frame, rsi_strategy)


class MAController(LifeController):
    """Starts and Stops MA rsi_strategies"""
    def __init__(self):
        super().__init__()

    def get_all_names(self):
        return self.account.get_ma_strategy()

    def delete_strategy(self, frame, index):
        strategy = self.account.get_ma_strategy().pop(index)
        self.execute(strategy)
        frame.update_list_box()

    def parameters_are_ok(self, frame, coin, dollar, order_type, account, take_profit, stop_loss, time_frame,
                          length, collateral):
        if not self.standard_parameters_are_ok(frame, coin, dollar, order_type, account, take_profit, stop_loss,
                                               time_frame, length, collateral):
            return False
        interval = {'length': [length, 1, 1000]}
        if not self.user_input_controller.is_in_interval(frame, interval):
            return False
        frame.show_error_massage("")
        return True

    def add_ma_rsi_strategy(self, frame, coin, dollar, order_type, account, take_profit, stop_loss,
                            time_frame, length, collateral):
        min_order_size = self.account.get_min_order_size(coin)
        if self.parameters_are_ok(frame, coin, dollar, order_type, account, take_profit, stop_loss, time_frame,
                                  length, collateral):
            values = self.login_controller.get_values(account)
            ma_strategy = self.account.new_ma_live(coin, float(dollar), order_type, float(min_order_size),
                                                   values, float(take_profit), float(stop_loss), time_frame,
                                                   float(length))
            self.bind_fsm(frame, ma_strategy)
