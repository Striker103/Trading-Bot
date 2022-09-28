from controller.ManuelTradingController import ManuelTradingController
from controller.LoginController import LoginController
from controller.UpdateController import UpdateController
from controller.UserInputController import UserInputController
from controller.HistoricalPricesController import HistoricalPricesController
from controller.LiveController import *
from controller.BacktestController import *
from model.Account import Account


class MainController:
    """ The controller that creates and knows all Controllers. Also, all Controllers know this controller. """
    def __init__(self):
        self.account = Account()
        self.historical_prices_controller = HistoricalPricesController()
        self.user_input_controller = UserInputController()
        self.manuel_trading_controller = ManuelTradingController()
        self.login_controller = LoginController()
        self.rsi_controller = RSIController()
        self.rsi_controller_backtest = RSIControllerBacktrack()
        self.update_controller = UpdateController()
        self.ma_controller = MAController()
        self.ma_controller_backtest = MAControllerBacktrack()

    def get_manuel_trading_controller(self):
        return self.manuel_trading_controller

    def get_login_controller(self):
        return self.login_controller

    def get_rsi_controller(self):
        return self.rsi_controller

    def get_rsi_controller_backtest(self):
        return self.rsi_controller_backtest

    def get_update_controller(self):
        return self.update_controller

    def get_user_input_controller(self):
        return self.user_input_controller

    def get_ma_controller(self):
        return self.ma_controller

    def get_ma_controller_backtest(self):
        return self.ma_controller_backtest

    def get_account(self):
        return self.account

    def set_account(self, account):
        self.account = account

    def set_account_everywhere(self):
        account = self.get_account()
        self.historical_prices_controller.set_account(account)
        self.user_input_controller.set_account(account)
        self.manuel_trading_controller.set_account(account)
        self.login_controller.set_account(account)
        self.rsi_controller.set_account(account)
        self.rsi_controller_backtest.set_account(account)
        self.update_controller.set_account(account)
        self.ma_controller.set_account(account)
        self.ma_controller_backtest.set_account(account)

    def get_historical_prices_controller(self):
        return self.historical_prices_controller

    def set_user_input_controller(self):
        self.get_rsi_controller().set_user_input_controller(self.get_user_input_controller())
        self.get_rsi_controller_backtest().set_user_input_controller(self.get_user_input_controller())
        self.get_ma_controller().set_user_input_controller(self.get_user_input_controller())
        self.get_ma_controller_backtest().set_user_input_controller(self.get_user_input_controller())
        self.get_manuel_trading_controller().set_user_input_controller(self.get_user_input_controller())

    def set_historical_prices_controller(self):
        self.get_rsi_controller_backtest().set_historical_prices_controller(self.get_historical_prices_controller())
        self.get_ma_controller_backtest().set_historical_prices_controller(self.get_historical_prices_controller())

    def set_login_controller(self):
        self.get_update_controller().set_login_controller(self.get_login_controller())
        self.get_ma_controller().set_login_controller(self.get_login_controller())
        self.get_rsi_controller().set_login_controller(self.get_login_controller())
        self.get_manuel_trading_controller().set_login_controller(self.get_login_controller())

    def set_update_controller(self):
        self.get_manuel_trading_controller().set_update_controller(self.get_update_controller())

    def get_self(self):
        return self

    def set_frames(self, frames):
        self.get_update_controller().set_frames(frames)
        self.get_login_controller().set_frames(frames)
