import tkinter as tk
from tkinter import END


class LoginData(tk.Frame):
    def __init__(self, main_controller, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.main_controller = main_controller
        self.login_Controller = self.main_controller.get_login_controller()
        self.configure(bg='gray30')

        tk.Label(self, text="Add an Account: ", bg='gray30', fg='white').place(x=120, y=40)

        tk.Label(self, text="name: ", bg='gray30', fg='white').place(x=120, y=70)
        self.api_name = tk.Entry(self, width=70, bg='gray40', fg='white')
        self.api_name.place(x=230, y=70)

        tk.Label(self, text="api_key: ", bg='gray30', fg='white').place(x=120, y=100)
        self.api_key = tk.Entry(self, width=70, bg='gray40', fg='white')
        self.api_key.place(x=230, y=100)

        tk.Label(self, text="api_secret: ", bg='gray30', fg='white').place(x=120, y=130)
        self.api_secret = tk.Entry(self, width=70, bg='gray40', fg='white')
        self.api_secret.place(x=230, y=130)

        tk.Label(self, text="sub account_name: ", bg='gray30', fg='white').place(x=120, y=160)
        self.sub_account_name = tk.Entry(self, width=70, bg='gray40', fg='white')
        self.sub_account_name.place(x=230, y=160)

        tk.Button(self, text="create", bg='gray30', fg='white', command=self.on_click_create).place(x=120, y=190)
        tk.Button(self, text="delete", bg='gray30', fg='white', command=self.on_click_delete).place(x=220, y=190)

        self.error_text_value = ""
        self.error_text = tk.Label(self, text=self.error_text_value, bg='gray30', fg='red')
        self.error_text.config(font=("arial bold", 12))
        self.error_text.place(x=130, y=220)

        self.listBox = tk.Listbox(self, bg='gray40', fg='white', width=125)
        self.listBox.place(x=20, y=300)
        self.refresh_list()

    def refresh_list(self):
        names = self.login_Controller.get_all_names()
        self.listBox.delete(0, END)
        for idx, name in enumerate(names):
            self.listBox.insert(idx, name)

    def on_click_create(self):
        self.login_Controller.create_account(self, self.api_name.get(), self.api_key.get(), self.api_secret.get(),
                                             self.sub_account_name.get())
        self.refresh_list()

    def show_error_massage(self, massage):
        self.error_text.config(text=massage)

    def on_click_delete(self):
        i = self.listBox.curselection()
        if len(i) != 0:
            self.error_text.config(text="")
            account_name = self.listBox.get(i)
            self.login_Controller.delete_account(account_name)
            self.refresh_list()
        else:
            self.error_text.config(text="no account selected")

    def menubar(self, root):
        menubar = tk.Menu(root)
        menubar.add_command(label="start", command=lambda: self.controller.show_frame("Start"))
        menubar.add_command(label="Add")
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
        menubar.add_command(label="Fomo Interval",
                            command=lambda: self.controller.show_frame("FomoTradingBacktestInterval"))
        return menubar
