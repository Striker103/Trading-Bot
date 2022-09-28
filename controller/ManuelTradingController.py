class ManuelTradingController:
    """ Responsible for handling manuel trades """
    def __init__(self):
        self.account = None
        self.login_controller = None
        self.user_input_controller = None
        self.update_controller = None

    def set_update_controller(self, update_controller):
        self.update_controller = update_controller

    def set_account(self, account):
        self.account = account

    def set_user_input_controller(self, user_input_controller):
        self.user_input_controller = user_input_controller

    def set_login_controller(self, login_controller):
        self.login_controller = login_controller

    def buy(self, frame, coin, dollar, order_type, account):
        """ buys dollar units of coin if account has enough free collateral """
        if not account:
            frame.show_error_massage("Please add an Account")
            return
        account_info = self.get_balance(account)
        free_collateral = account_info['freeCollateral'] * account_info['leverage']
        frame.show_error_massage("")
        if self.parameters_are_ok(frame, coin, dollar, order_type, account):
            strategy = self.get_trading_strategy_if_it_exists(coin)
            if strategy:
                strategy.set_order_type(order_type)
                if self.order_size_big_enough(frame, strategy, dollar):
                    if strategy.get_side() == "long":
                        if self.has_enough_collateral(frame, dollar, free_collateral):
                            # side is long and it gets bigger
                            response = self.place_position(strategy, dollar, "buy")
                            if response:
                                strategy.set_size(strategy.get_size() + response['size'])
                    else:
                        # side is short and it gets smaller
                        if strategy.get_position_value() > float(dollar):
                            response = self.place_position(strategy, dollar, "buy")
                            strategy.set_size(strategy.get_size() + response['size'])
                            if strategy.get_size() == 0:
                                del strategy
                        else:
                            if self.has_enough_collateral_after_size(frame, dollar, free_collateral, strategy):
                                # side is switched from short to long
                                response = self.place_position(strategy, float(dollar), "buy")
                                strategy.set_size(strategy.get_size() + response['size'])
                                strategy.set_side("long")
                                if strategy.get_size() == 0:
                                    del strategy
            else:
                self.create_strategy(frame, coin, dollar, order_type, account, free_collateral, "long")
        frame.update_list_box()
        self.update_controller.get_balance(frame, account)

    def sell(self, frame, coin, dollar, order_type, account):
        """ sells dollar units of coin if account has enough free collateral """
        if not account:
            frame.show_error_massage("Please add an Account")
            return
        account_info = self.get_balance(account)
        free_collateral = account_info['freeCollateral'] * account_info['leverage']
        frame.show_error_massage("")
        if self.parameters_are_ok(frame, coin, dollar, order_type, account):
            strategy = self.get_trading_strategy_if_it_exists(coin)
            if strategy:
                strategy.set_order_type(order_type)
                if self.order_size_big_enough(frame, strategy, dollar):
                    if strategy.get_side() == "short":
                        if self.has_enough_collateral(frame, dollar, free_collateral):
                            # side is short and it gets bigger
                            response = self.place_position(strategy, dollar, "sell")
                            if response:
                                strategy.set_size(strategy.get_size() - response['size'])
                    else:
                        # side is long and it gets smaller
                        if strategy.get_position_value() > float(dollar):
                            response = self.place_position(strategy, dollar, "sell")
                            strategy.set_size(strategy.get_size() - response['size'])
                            if strategy.get_size() == 0:
                                del strategy
                        else:
                            if self.has_enough_collateral_after_size(frame, dollar, free_collateral, strategy):
                                # side is switched from long to short
                                response = self.place_position(strategy, float(dollar), "sell")
                                strategy.set_size(strategy.get_size() - response['size'])
                                strategy.set_side("short")
                                if strategy.get_size() == 0:
                                    del strategy
                                    frame.update_list_box()
            else:
                self.create_strategy(frame, coin, dollar, order_type, account, free_collateral, "short")
        frame.update_list_box()
        self.update_controller.get_balance(frame, account)

    def get_balance(self, account_name):
        return self.update_controller.give_balance(account_name)

    @staticmethod
    def place_position(strategy, dollar, action):
        if strategy.order_type == "Market":
            response = strategy.place_order.buy_sell_market(action, strategy.calculate_quantity_to_buy(dollar))
        else:
            response = strategy.place_order.buy_sell_limit_rebalance(action,
                                                                     strategy.calculate_quantity_to_buy(dollar))
        return response

    def order_size_big_enough(self, frame, strategy, dollar):
        """ checks if order size is bigger then minimum order size of the exchange """
        min_order_size = self.account.get_min_order_size(strategy.coin)
        if float(strategy.calculate_quantity_to_buy(dollar)) < float(min_order_size):
            frame.show_error_massage("order size is to small")
            return False
        return True

    def create_strategy(self, frame, coin, dollar, order_type, account, free_collateral, side):
        """ creates a new manuel strategy and buys/sells dollar units of coin if account has enough
         free_collateral """
        if self.has_enough_collateral(frame, dollar, free_collateral):
            min_order_size = self.account.get_min_order_size(coin)
            values = self.login_controller.get_values(account)
            strategy = self.account.new_manuel_trading(coin, dollar, order_type, min_order_size, values)
            if self.order_size_big_enough(frame, strategy, dollar):
                if side == "long":
                    response = self.place_position(strategy, dollar, "buy")
                    strategy.set_side("long")
                    strategy.set_size(response['size'])
                else:
                    response = self.place_position(strategy, dollar, "sell")
                    strategy.set_side("short")
                    strategy.set_size((-1) * response['size'])
                frame.update_list_box()

    def get_trading_strategy_if_it_exists(self, coin):
        return self.account.get_manuel_strategy(coin)

    def get_all_names(self):
        strategies = self.account.get_active_manuel_strategies()
        return strategies

    def delete_strategy(self, frame, index, order_type, account):
        if not self.order_type_and_account_selected(frame, order_type, account):
            return
        strategy = self.account.delete_manuel_strategy_index(index)
        strategy.set_order_type(order_type)
        strategy.close_position()
        frame.update_list_box()

    def parameters_are_ok(self, frame, coin, dollar, order_type, account):
        if not self.user_input_controller.coin_exists(frame, coin):
            return False
        selected = {'order_type': order_type, 'account': account}
        if not self.user_input_controller.values_are_selected(frame, selected):
            return False
        values = {'dollar': dollar}
        if not self.user_input_controller.is_a_float(frame, values):
            return False
        floats = {'dollar': dollar}
        if not self.user_input_controller.is_positive(frame, floats):
            return False
        if not self.user_input_controller.order_size_is_big_enough(frame, coin, dollar):
            return False
        return True

    def order_type_and_account_selected(self, frame, order_type, account):
        selected = {'order_type': order_type, 'account': account}
        if not self.user_input_controller.values_are_selected(frame, selected):
            return False
        return True

    def has_enough_collateral(self, frame, dollar, free_collateral):
        if not self.user_input_controller.enough_collateral(frame, dollar, free_collateral):
            return False
        return True

    def has_enough_collateral_after_size(self, frame, dollar, free_collateral, strategy):
        """ if an account has for example 100 dollar collateral and a BTC short position with a value of
         50 dollar. And now the user want to buy 140 dollar in btc. He can do this because the 50 dollar value of the
         short position + 100 dollar collateral are 150 dollar > 140 dollar. This method checks this"""
        position_value = strategy.get_position_value()
        new_dollar = float(dollar) - position_value
        new_free_collateral = free_collateral + position_value
        if not self.user_input_controller.enough_collateral(frame, new_dollar, new_free_collateral):
            return False
        return True
