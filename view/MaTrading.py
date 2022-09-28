import tkinter as tk
from tkinter import END


class MaTrading(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.login_Controller = main_controller.get_login_controller()
        self.update_controller = main_controller.get_update_controller()
        self.ma_trading = main_controller.get_ma_controller()
        self.configure(background='gray30')

        ma_strategies = main_controller.get_account().get_ma_strategy()
        for strategy in ma_strategies:
            strategy.frame = self

        tk.Label(self, text="Coin: ", bg='gray30', fg='white').place(x=130, y=50)
        self.user_input_coin = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_coin.place(x=230, y=50)

        tk.Label(self, text="dollar: ", bg='gray30', fg='white').place(x=130, y=80)
        self.user_input_dollar = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_dollar.place(x=230, y=80)

        options_list_order_types = ["Limit", "Market"]
        self.user_selected_order_type = tk.StringVar(self)
        self.user_selected_order_type.set("Select an Option")
        question_menu = tk.OptionMenu(self, self.user_selected_order_type, *options_list_order_types)
        question_menu.place(x=230, y=110)
        question_menu.config(bg='gray40', fg='white')
        tk.Label(self, text="order Type: ", bg='gray30', fg='white').place(x=130, y=110)

        self.select_account = tk.StringVar(self)

        options_list_time_frames = ["1min", "5min", "15min", "1h", "4h", "1day"]
        self.time_frame = tk.StringVar(self)
        self.time_frame.set("Select an Option")
        question_menu = tk.OptionMenu(self, self.time_frame, *options_list_time_frames)
        question_menu.place(x=230, y=170)
        question_menu.config(bg='gray40', fg='white')
        tk.Label(self, text="time frame: ", bg='gray30', fg='white').place(x=130, y=170)

        tk.Label(self, text="length:", bg='gray30', fg='white').place(x=130, y=200)
        self.user_input_length = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_length.place(x=230, y=200)

        tk.Label(self, text="take profit: ", bg='gray30', fg='white').place(x=400, y=50)
        self.user_input_take_profit = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_take_profit.place(x=550, y=50)

        tk.Label(self, text="stop loss: ", bg='gray30', fg='white').place(x=400, y=80)
        self.user_input_stop_loss = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_stop_loss.place(x=550, y=80)

        tk.Label(self, text="Total collateral: ", bg='gray30', fg='white').place(x=400, y=110)
        self.total_collateral_value = ""
        self.total_collateral_text = tk.Label(self, text=self.total_collateral_value, bg='gray30', fg='white')
        self.total_collateral_text.place(x=550, y=110)

        tk.Label(self, text="Free collateral: ", bg='gray30', fg='white').place(x=400, y=140)
        self.free_collateral_value = ""
        self.free_collateral_text = tk.Label(self, text=self.free_collateral_value, bg='gray30', fg='white')
        self.free_collateral_text.place(x=550, y=140)

        tk.Label(self, text="leverage: ", bg='gray30', fg='white').place(x=400, y=170)
        self.leverage_value = ""
        self.leverage_text = tk.Label(self, text=self.leverage_value, bg='gray30', fg='white')
        self.leverage_text.place(x=550, y=170)

        self.listBox = tk.Listbox(self, bg='gray40', fg='white', width=125)
        self.listBox.place(x=20, y=300)

        self.free_collateral = 0
        self.total_collateral = 0
        self.leverage = 0

        tk.Button(self, bg='gray30', fg='white', text="Start Trading Bot",
                  command=self.on_click_start).place(x=130, y=250)
        tk.Button(self, bg='gray30', fg='white', text="Stop Trading Bot",
                  command=self.on_click_close_position).place(x=260, y=250)

        self.error_text_value = ""
        self.error_text = tk.Label(self, text=self.error_text_value, bg='gray30', fg="red")
        self.error_text.place(x=380, y=250)
        self.error_text.config(font=("arial bold", 12))

        self.update_select_account_list()

    def update_select_account_list(self):
        names = self.login_Controller.get_all_names()
        if names:
            self.select_account.set("Select an Option")
            question_menu = tk.OptionMenu(self, self.select_account, *names, command=self.display_balance)
            question_menu.place(x=230, y=140)
            question_menu.config(bg='gray40', fg='white')
            tk.Label(self, text="select account: ", bg='gray30', fg='white').place(x=130, y=140)

    def menubar(self, root):
        menubar = tk.Menu(root)
        menubar.add_command(label="start", command=lambda: self.controller.show_frame("Start"))
        menubar.add_command(label="Add", command=lambda: self.controller.show_frame("LoginData"))
        menubar.add_command(label="Manuel", command=lambda: self.controller.show_frame("ManuelTrading"))
        menubar.add_command(label="RSI", command=lambda: self.controller.show_frame("RSITrading"))
        menubar.add_command(label="RSI Backtest",
                            command=lambda: self.controller.show_frame("RSITradingBacktest"))
        menubar.add_command(label="RSI Interval",
                            command=lambda: self.controller.show_frame("RSITradingBacktestInterval"))
        menubar.add_command(label="MA")
        menubar.add_command(label="MA Backtest", command=lambda: self.controller.show_frame("MaTradingBacktest"))
        menubar.add_command(label="MA Interval",
                            command=lambda: self.controller.show_frame("MaTradingBacktestInterval"))
        menubar.add_command(label="Fomo", command=lambda: self.controller.show_frame("Fomo"))
        menubar.add_command(label="Fomo Backtest", command=lambda: self.controller.show_frame("FomoTradingBacktest"))
        menubar.add_command(label="Fomo Interval",
                            command=lambda: self.controller.show_frame("FomoTradingBacktestInterval"))
        return menubar

    def update_list_box(self):
        strategies = self.ma_trading.get_all_names()
        self.listBox.delete(0, END)
        for idx, strategy in enumerate(strategies):
            self.listBox.insert(idx, strategy)

    def display_balance(self, account_name):
        if not account_name == "Please add an Account":
            self.update_controller.get_balance(self, account_name)

    def set_balance(self, balance):
        self.total_collateral = float(balance['collateral'])
        self.free_collateral = float(balance['freeCollateral'])
        self.leverage = int(balance['leverage'])
        self.total_collateral_text.config(text=str(round(float(balance['collateral']), 2)) + "$")
        self.free_collateral_text.config(text=str(round(float(balance['freeCollateral']), 2)) + "$")
        self.leverage_text.config(text=str(balance['leverage']) + "x")

    def on_click_close_position(self):
        i = self.listBox.curselection()
        for index in i:
            self.ma_trading.delete_strategy(self, index)

    def show_error_massage(self, massage):
        self.error_text.config(text=massage)

    def on_click_start(self):
        self.ma_trading.add_ma_rsi_strategy(self,
                                            self.user_input_coin.get(),
                                            self.user_input_dollar.get(),
                                            self.user_selected_order_type.get(),
                                            self.select_account.get(),
                                            self.user_input_take_profit.get(),
                                            self.user_input_stop_loss.get(),
                                            self.time_frame.get(),
                                            self.user_input_length.get(),
                                            self.total_collateral)
