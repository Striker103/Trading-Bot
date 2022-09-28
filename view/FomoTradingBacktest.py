import tkinter as tk
from tkinter import END


class FomoTradingBacktest(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ma_trading_backtest = main_controller.get_ma_controller_backtest()
        self.configure(bg='gray30')

        ma_backtest_strategies = main_controller.get_account().get_ma_backtest_strategy()
        for strategy in ma_backtest_strategies:
            strategy.frame = self

        tk.Label(self, text="Coin: ", bg='gray30', fg='white').place(x=130, y=50)
        self.user_input_coin = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_coin.place(x=230, y=50)

        tk.Label(self, text="dollar: ", bg='gray30', fg='white').place(x=130, y=80)
        self.user_input_dollar = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_dollar.place(x=230, y=80)

        tk.Label(self, text="time frame: ", bg='gray30', fg='white').place(x=130, y=110)
        self.user_input_time_frame = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_time_frame.place(x=230, y=110)

        tk.Label(self, text="length: ", bg='gray30', fg='white').place(x=130, y=140)
        self.user_input_length = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_length.place(x=230, y=140)

        tk.Label(self, text="name of file: ", bg='gray30', fg='white').place(x=130, y=170)
        self.user_input_name_of_file = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_name_of_file.place(x=230, y=170)

        tk.Label(self, text="take profit: ", bg='gray30', fg='white').place(x=400, y=50)
        self.user_input_take_profit = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_take_profit.place(x=550, y=50)

        tk.Label(self, text="stop loss: ", bg='gray30', fg='white').place(x=400, y=80)
        self.user_input_stop_loss = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_stop_loss.place(x=550, y=80)

        tk.Label(self, text="trading fees: ", bg='gray30', fg='white').place(x=400, y=110)
        self.user_input_trading_fees = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_trading_fees.place(x=550, y=110)

        tk.Label(self, text="days to backtest(1-365): ", bg='gray30', fg='white').place(x=400, y=140)
        self.user_input_days = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_days.place(x=550, y=140)

        self.error_text_value = ""
        self.error_text = tk.Label(self, text=self.error_text_value, bg='gray30', fg='red')
        self.error_text.config(font=("arial bold", 12))
        self.error_text.place(x=130, y=220)

        tk.Button(self, bg='gray30', fg='white', text="Start Backtesting",
                  command=self.on_click_start_backtesting).place(x=130, y=250)
        tk.Button(self, bg='gray30', fg='white', text="Delete Backtest",
                  command=self.on_click_delete_backtest).place(x=240, y=250)
        tk.Button(self, bg='gray30', fg='white', text="Delete all Tests",
                  command=self.on_click_delete_all).place(x=340, y=250)

        self.listBox = tk.Listbox(self, width=125, bg='gray40', fg='white')
        self.listBox.place(x=20, y=300)

        self.update_list_box()

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
        menubar.add_command(label="MA", command=lambda: self.controller.show_frame("MaTrading"))
        menubar.add_command(label="MA Backtest", command=lambda: self.controller.show_frame("MaTradingBacktest"))
        menubar.add_command(label="MA Interval",
                            command=lambda: self.controller.show_frame("MaTradingBacktestInterval"))
        menubar.add_command(label="Fomo", command=lambda: self.controller.show_frame("Fomo"))
        menubar.add_command(label="Fomo Backtest")
        menubar.add_command(label="Fomo Interval",
                            command=lambda: self.controller.show_frame("FomoTradingBacktestInterval"))
        return menubar

    def update_list_box(self):
        strategies = self.ma_trading_backtest.get_all_ma_backtest_strategies()
        self.listBox.delete(0, END)
        for idx, strategy in enumerate(strategies):
            self.listBox.insert(idx, strategy)

    def on_click_delete_backtest(self):
        index = self.listBox.curselection()
        for i in index:
            self.ma_trading_backtest.delete_strategy(self, i)
        self.update_list_box()

    def on_click_delete_all(self):
        self.ma_trading_backtest.delete_all_strategies(self)
        self.update_list_box()

    def show_error_massage(self, massage):
        self.error_text.config(text=massage)

    def on_click_start_backtesting(self):
        self.ma_trading_backtest.start_single_backtest(self,
                                                       self.user_input_coin.get(),
                                                       self.user_input_dollar.get(),
                                                       self.user_input_time_frame.get(),
                                                       self.user_input_length.get(),
                                                       self.user_input_name_of_file.get(),
                                                       self.user_input_take_profit.get(),
                                                       self.user_input_stop_loss.get(),
                                                       self.user_input_trading_fees.get(),
                                                       self.user_input_days.get())

        self.update_list_box()
