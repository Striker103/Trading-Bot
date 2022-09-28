import tkinter as tk


class Start(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        self.var = tk.StringVar()
        self.var.set(str(10))
        self.controller = controller
        self.main_controller = main_controller
        self.update_controller = main_controller.get_update_controller()
        self.login_controller = main_controller.get_login_controller()
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background='gray30')

        tk.Label(self, text="changes the time (in seconds) in which current Market datas are "
                            "fetched (prices, rsi, etc)", bg='gray30', fg='white').place(x=130, y=100)
        self.user_input_time = tk.Entry(self, bg='gray40', fg='white')
        self.user_input_time.place(x=190, y=130)
        tk.Button(self, text="adjust time", bg='gray30', fg='white', command=self.on_click_new_time).place(x=320, y=128)
        tk.Label(self, text="time:", bg='gray30', fg='white').place(x=130, y=130)
        tk.Label(self, textvariable=self.var, bg='gray30', fg='white').place(x=160, y=130)

        tk.Button(self, text="load", bg='gray30', fg='white', command=self.on_click_load).place(x=130, y=200)
        tk.Button(self, text="save", bg='gray30', fg='white', command=self.on_click_save).place(x=180, y=200)

    def menubar(self, root):
        menubar = tk.Menu(root)
        menubar.add_command(label="start")
        menubar.add_command(label="Add", command=lambda: self.controller.show_frame("LoginData"))
        menubar.add_command(label="Manuel", command=lambda: self.controller.show_frame("ManuelTrading"))
        menubar.add_command(label="RSI", command=lambda: self.controller.show_frame("RSITrading"))
        menubar.add_command(label="RSI Backtest", command=lambda: self.controller.show_frame("RSITradingBacktest"))
        menubar.add_command(label="RSIInterval",
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

    def on_click_load(self):
        self.login_controller.load()

    def on_click_save(self):
        self.login_controller.save()

    def on_click_new_time(self):
        if self.isfloat(self.user_input_time.get()):
            if float(self.user_input_time.get()) < 0.1:
                return
            self.update_controller.update_time(float(self.user_input_time.get()))
            self.var.set(self.user_input_time.get())

    @staticmethod
    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False
