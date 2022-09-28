import tkinter as tk
from threading import Thread
from tkinter import END


class ManuelTrading(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.main_controller = main_controller
        self.login_Controller = self.main_controller.get_login_controller()
        self.manuel_trading = self.main_controller.get_manuel_trading_controller()
        self.update_controller = self.main_controller.get_update_controller()
        self.configure(bg='gray30')

        manuel_strategies = main_controller.get_account().get_active_manuel_strategies()
        for strategy in manuel_strategies:
            strategy.frame = self

        tk.Label(self, text="Coin: ", bg='gray30', fg='white').place(x=130, y=50)
        self.user_input_coin = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_coin.place(x=230, y=50)

        tk.Label(self, text="dollar: ", bg='gray30', fg='white').place(x=130, y=80)
        self.user_input_money = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_money.place(x=230, y=80)

        options_list = ["Limit", "Market"]
        self.user_selected_order_type = tk.StringVar(self)
        self.user_selected_order_type.set("Select an Option")
        question_menu = tk.OptionMenu(self, self.user_selected_order_type, *options_list)
        question_menu.place(x=230, y=110)
        question_menu.config(bg='gray40', fg='white')
        tk.Label(self, text="order Type: ", bg='gray30', fg='white').place(x=130, y=110)

        self.select_account = tk.StringVar(self)

        tk.Label(self, text="Total collateral: ", bg='gray30', fg='white').place(x=400, y=80)
        self.total_collateral_value = ""
        self.total_collateral_text = tk.Label(self, text=self.total_collateral_value, bg='gray30', fg='white')
        self.total_collateral_text.place(x=550, y=80)

        tk.Label(self, text="Free collateral: ", bg='gray30', fg='white').place(x=400, y=110)
        self.free_collateral_value = ""
        self.free_collateral_text = tk.Label(self, text=self.free_collateral_value, bg='gray30', fg='white')
        self.free_collateral_text.place(x=550, y=110)

        tk.Label(self, text="leverage: ", bg='gray30', fg='white').place(x=400, y=140)
        self.leverage_value = ""
        self.leverage_text = tk.Label(self, text=self.leverage_value, bg='gray30', fg='white')
        self.leverage_text.place(x=550, y=140)

        self.free_collateral = 0
        self.total_collateral = 0
        self.leverage = 0

        self.listBox = tk.Listbox(self, width=125, bg='gray40', fg='white')
        self.listBox.place(x=20, y=300)

        tk.Button(self, text="buy", bg='gray30', fg='white', command=self.on_click_buy).place(x=130, y=250)
        tk.Button(self, text="sell", bg='gray30', fg='white', command=self.on_click_sell).place(x=180, y=250)

        tk.Button(self, text="close Position", bg='gray30', fg='white',
                  command=self.on_click_close_position).place(x=230, y=250)

        self.error_text_value = ""
        self.error_text = tk.Label(self, text=self.error_text_value, bg='gray30', fg='red')
        self.error_text.config(font=("arial bold", 12))
        self.error_text.place(x=130, y=220)

        self.update_select_account_list()

    def on_click_close_position(self):
        i = self.listBox.curselection()
        for index in i:
            def sell():
                self.manuel_trading.delete_strategy(self, index,
                                                    self.user_selected_order_type.get(),
                                                    self.select_account.get())
            t1 = Thread(target=sell)
            t1.daemon = True
            t1.start()

    def update_list_box(self):
        strategies = self.manuel_trading.get_all_names()
        self.listBox.delete(0, END)
        for idx, strategy in enumerate(strategies):
            self.listBox.insert(idx, strategy)

    def show_error_massage(self, massage):
        self.error_text.config(text=massage)

    def menubar(self, root):
        menubar = tk.Menu(root)
        menubar.add_command(label="start", command=lambda: self.controller.show_frame("Start"))
        menubar.add_command(label="Add", command=lambda: self.controller.show_frame("LoginData"))
        menubar.add_command(label="Manuel")
        menubar.add_command(label="RSI", command=lambda: self.controller.show_frame("RSITrading"))
        menubar.add_command(label="RSI Backtest",
                            command=lambda: self.controller.show_frame("RSITradingBacktest"))
        menubar.add_command(label="RSI Interval",
                            command=lambda: self.controller.show_frame("RSITradingBacktestInterval"))
        menubar.add_command(label="MA", command=lambda: self.controller.show_frame("MaTrading"))
        menubar.add_command(label="MA Backtest", command=lambda: self.controller.show_frame("MaTradingBacktest"))
        menubar.add_command(label="MA Interval",
                            command=lambda: self.controller.show_frame("MaTradingBacktestInterval"))
        menubar.add_command(label="Fomo", command=lambda: self.controller.show_frame("Fomo"))
        menubar.add_command(label="Fomo Backtest", command=lambda: self.controller.show_frame("FomoTradingBacktest"))
        menubar.add_command(label="Fomo Interval",
                            command=lambda: self.controller.show_frame("FomoTradingBacktestInterval"))
        return menubar

    def update_select_account_list(self):
        names = self.login_Controller.get_all_names()
        if names:
            self.select_account.set("Select an Option")
            self.select_account.set(self.select_account.get())
            question_menu = tk.OptionMenu(self, self.select_account, *names, command=self.display_balance)
            question_menu.place(x=230, y=140)
            question_menu.config(bg='gray40', fg='white')
            tk.Label(self, text="select account: ", bg='gray30', fg='white').place(x=130, y=140)

    def on_click_buy(self):
        def buy():
            self.manuel_trading.buy(self,
                                    self.user_input_coin.get(),
                                    self.user_input_money.get(),
                                    self.user_selected_order_type.get(),
                                    self.select_account.get())
        t1 = Thread(target=buy)
        t1.daemon = True
        t1.start()

    def on_click_sell(self):
        def sell():
            self.manuel_trading.sell(self,
                                     self.user_input_coin.get(),
                                     self.user_input_money.get(),
                                     self.user_selected_order_type.get(),
                                     self.select_account.get())
        t1 = Thread(target=sell)
        t1.daemon = True
        t1.start()

    def display_balance(self, account_name):
        self.update_controller.get_balance(self, account_name)

    def set_balance(self, balance):
        self.total_collateral = float(balance['collateral'])
        self.free_collateral = float(balance['freeCollateral'])
        self.leverage = int(balance['leverage'])
        self.total_collateral_text.config(text=str(round(float(balance['collateral']), 2)) + "$")
        self.free_collateral_text.config(text=str(round(float(balance['freeCollateral']), 2)) + "$")
        self.leverage_text.config(text=str(balance['leverage']) + "x")
