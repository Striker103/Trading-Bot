import tkinter as tk
from tkinter import font as tk_font
from view.Start import Start
from view.ManuelTrading import ManuelTrading
from view.LoginData import LoginData
from view.RSITrading import RSITrading
from controller.MainController import MainController
from view.RSITradingBacktest import RSITradingBacktest
from view.RSITradingBacktestInterval import RSITradingBacktestInterval
from view.MaTrading import MaTrading
from view.MaTradingBacktest import MaTradingBacktest
from view.MaTradingBacktestInterval import MaTradingBacktestInterval
from view.Fomo import Fomo
from view.FomoTradingBacktest import FomoTradingBacktest
from view.FomoTradingBacktestInterval import FomoTradingBacktestInterval

"""
    Title: Switch between two frames in tkinter ?
    Author: Bryan Oakley
    Date: 2011
    Availability: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
    """


class Frames(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.frames = {}

        self.main_Controller = MainController()
        self.main_Controller.set_user_input_controller()
        self.main_Controller.set_historical_prices_controller()
        self.main_Controller.set_account_everywhere()
        self.main_Controller.set_login_controller()
        self.main_Controller.set_update_controller()
        self.main_Controller.set_frames(self.frames)

        self.title_font = tk_font.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.title("Algorithmic Trading")
        self.geometry("800x500")

        for F in (Start, ManuelTrading, LoginData, RSITrading, RSITradingBacktest, RSITradingBacktestInterval,
                  MaTrading, MaTradingBacktest, MaTradingBacktestInterval, Fomo, FomoTradingBacktest,
                  FomoTradingBacktestInterval):
            page_name = F.__name__
            frame = F(self.main_Controller, parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        update_controller = self.main_Controller.get_update_controller()
        update_controller.update()
        self.show_frame("Start")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        menubar = frame.menubar(self)
        self.configure(menu=menubar, background='blue')

    def get_main_controller(self):
        return self.main_Controller


if __name__ == "__main__":
    app = Frames()
    app.mainloop()
