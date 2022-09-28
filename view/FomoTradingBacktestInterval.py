import tkinter as tk


class FomoTradingBacktestInterval(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.ma_trading_backtest = main_controller.get_ma_controller_backtest()
        self.configure(bg='gray30')

        tk.Label(self, text="dollar: ", bg='gray30', fg='white').place(x=130, y=50)
        self.user_input_dollar = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_dollar.place(x=230, y=50)

        tk.Label(self, text="name of file: ", bg='gray30', fg='white').place(x=130, y=80)
        self.user_input_name_of_file = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_name_of_file.place(x=230, y=80)

        tk.Label(self, text="Coin: ", bg='gray30', fg='white').place(x=130, y=110)
        self.user_input_coin = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_coin.place(x=230, y=110)

        tk.Label(self, text="time frame: ", bg='gray30', fg='white').place(x=130, y=140)
        self.user_input_time_frame = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_time_frame.place(x=230, y=140)

        tk.Label(self, text="trading fees: ", bg='gray30', fg='white').place(x=130, y=170)
        self.user_input_trading_fees = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_trading_fees.place(x=230, y=170)

        tk.Label(self, text="Coin, time frame and trading fees can bee \n comma separated e.g.: BTC,ETH,SOL",
                 bg='gray30', fg='white').place(x=130, y=200)

        tk.Label(self, text="lower", bg='gray30', fg='white').place(x=550, y=30)
        tk.Label(self, text="upper", bg='gray30', fg='white').place(x=625, y=30)
        tk.Label(self, text="interval", bg='gray30', fg='white').place(x=700, y=30)

        tk.Label(self, text="take profit: ", bg='gray30', fg='white').place(x=400, y=50)
        self.user_input_take_profit_lower = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_take_profit_lower.place(x=550, y=50)
        self.user_input_take_profit_upper = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_take_profit_upper.place(x=625, y=50)
        self.user_input_take_profit_interval = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_take_profit_interval.place(x=700, y=50)

        tk.Label(self, text="stop loss: ", bg='gray30', fg='white').place(x=400, y=80)
        self.user_input_stop_loss_lower = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_stop_loss_lower.place(x=550, y=80)
        self.user_input_stop_loss_upper = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_stop_loss_upper.place(x=625, y=80)
        self.user_input_stop_loss_interval = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_stop_loss_interval.place(x=700, y=80)

        tk.Label(self, text="days to backtest(1-365): ", bg='gray30', fg='white').place(x=400, y=110)
        self.user_input_days_lower = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_days_lower.place(x=550, y=110)
        self.user_input_days_upper = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_days_upper.place(x=625, y=110)
        self.user_input_days_interval = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_days_interval.place(x=700, y=110)

        tk.Label(self, text="length(1-1000): ", bg='gray30', fg='white').place(x=400, y=140)
        self.user_input_length_lower = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_length_lower.place(x=550, y=140)
        self.user_input_length_upper = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_length_upper.place(x=625, y=140)
        self.user_input_length_interval = tk.Entry(self, bg='gray40', fg='white', width=10)
        self.user_input_length_interval.place(x=700, y=140)

        tk.Label(self, text="Example: take profit lower = 1.5, upper = 2.25, interval = 0.25 \n means backtest will "
                            "be done with 1.5,1.75,2.0 and 2.25", bg='gray30', fg='white').place(x=400, y=160)

        self.error_text_value = ""
        self.error_text = tk.Label(self, text=self.error_text_value, bg='gray30', fg='red')
        self.error_text.config(font=("arial bold", 12))
        self.error_text.place(x=130, y=275)

        self.run_text_value = ""
        self.run_text = tk.Label(self, text=self.run_text_value, bg='gray30', fg='white')
        self.run_text.place(x=450, y=280)
        self.run_text.config(font=("Courier", 12))

        tk.Button(self, bg='gray30', fg='white', text="Start Backtesting",
                  command=self.on_click_start_backtesting).place(x=130, y=250)
        tk.Button(self, bg='gray30', fg='white', text="Stop Backtest",
                  command=self.on_click_delete_backtest).place(x=240, y=250)

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
        menubar.add_command(label="Fomo Backtest", command=lambda: self.controller.show_frame("FomoTradingBacktest"))
        menubar.add_command(label="Fomo Interval")
        return menubar

    def on_click_delete_backtest(self):
        self.run_text.config(text="stopping: please wait")
        self.ma_trading_backtest.stop = True

    def show_error_massage(self, massage):
        self.error_text.config(text=massage)

    def show_current_run(self, massage):
        self.run_text.config(text=massage)

    def on_click_start_backtesting(self):
        self.ma_trading_backtest.start_multiple_backtest(self,
                                                         self.user_input_dollar.get(),
                                                         self.user_input_name_of_file.get(),
                                                         self.user_input_coin.get(),
                                                         self.user_input_time_frame.get(),
                                                         self.user_input_trading_fees.get(),
                                                         self.user_input_take_profit_lower.get(),
                                                         self.user_input_take_profit_upper.get(),
                                                         self.user_input_take_profit_interval.get(),
                                                         self.user_input_stop_loss_lower.get(),
                                                         self.user_input_stop_loss_upper.get(),
                                                         self.user_input_stop_loss_interval.get(),
                                                         self.user_input_days_lower.get(),
                                                         self.user_input_days_upper.get(),
                                                         self.user_input_days_interval.get(),
                                                         self.user_input_length_lower.get(),
                                                         self.user_input_length_upper.get(),
                                                         self.user_input_length_interval.get())
