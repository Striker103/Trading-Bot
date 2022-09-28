import pathlib
import pickle


class LoginController:
    """ Handles user Login data and saves and stores strategies """
    def __init__(self):
        self.account = None
        self.frames = None
        self.PATH_OF_THIS_FILE = pathlib.Path(__file__)
        self.PATH_TO_RESULTS = pathlib.Path(__file__).parent.joinpath('results')

    def set_account(self, account):
        self.account = account

    def set_frames(self, frames):
        self.frames = frames

    def load(self):
        """ Loads all saved strategies if they exist """
        try:
            pkl_file = open(self.PATH_TO_RESULTS.joinpath('Pickle').joinpath('strategies.pkl'), 'rb')
            strategy = pickle.load(pkl_file)
            self.account.extend_all_active_strategies(strategy)
            self.frames['ManuelTrading'].update_list_box()
            self.frames['RSITrading'].update_list_box()
            self.frames['RSITradingBacktest'].update_list_box()
            self.frames['MaTrading'].update_list_box()
            self.frames['MaTradingBacktest'].update_list_box()
        except FileNotFoundError:
            pass

    def save(self):
        """ saves all lists of strategies in strategies.pkl """
        output = open(self.PATH_TO_RESULTS.joinpath('Pickle').joinpath('strategies.pkl'), 'wb')
        pickle.dump(self.account.get_all_active_strategies(), output)
        output.close()

    def check_user_input(self, frame, name, api_key, api_secret):
        if name == "":
            frame.show_error_massage("api name cant be empty")
            return False

        if api_key == "":
            frame.show_error_massage("api_key cant be empty")
            return False

        if api_secret == "":
            frame.show_error_massage("api secret cant be empty")
            return False

        names = self.get_all_names()
        for n in names:
            if name == n:
                frame.show_error_massage("there is already an account with this name")
                return False
        return True

    def try_to_get_account_information(self, frame, api_key, api_secret, sub_account_name):
        """ If a user wants to add a new account an API account balance call with the user inputs  is placed.
        Depending on different wrong user inputs the API gives back the following errors they are shown to the user
        then and now account is added"""
        values = [api_key, api_secret]
        if sub_account_name:
            values.append(sub_account_name)
        try:
            self.account.get_balance(values)
        except Exception as e:
            frame.show_error_massage(e)
            return False
        else:
            frame.show_error_massage("")
            return True

    def create_account(self, frame, name, api_key, api_secret, sub_account_name=None):
        """ creates a new account if the user inputs are valid and saves them """
        if not self.check_user_input(frame, name, api_key, api_secret):
            return
        if not self.try_to_get_account_information(frame, api_key, api_secret, sub_account_name):
            return
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "a") as text_file:
            text_file.write(name + ":")
            text_file.write(api_key + ":")
            text_file.write(api_secret + ":")
            text_file.write(sub_account_name)
            text_file.write('\n')

        # updates the select_account widgets so the new account is immediately shown
        self.frames['ManuelTrading'].update_select_account_list()
        self.frames['RSITrading'].update_select_account_list()
        self.frames['MaTrading'].update_select_account_list()

    def read_file(self):
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "r") as text_file:
            print(text_file.read())

    def get_all_names(self):
        """ returns all names of all existing accounts """
        names = []
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "r") as text_file:
            for line in text_file:
                things = line.split(':')
                names.append(things[0])
        return names

    def delete_account(self, name):
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "r") as text_file:
            lines = text_file.readlines()
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "w") as text_file:
            for line in lines:
                values = line.split(':')
                if not values[0] == name:
                    text_file.write(line)
        self.frames['ManuelTrading'].update_select_account_list()
        self.frames['RSITrading'].update_select_account_list()
        self.frames['MaTrading'].update_select_account_list()

    def get_values(self, name):
        """ returns api key and api secret of the account with this name """
        values = []
        with open(self.PATH_TO_RESULTS.joinpath('Login Data').joinpath('Accounts.txt'), "r") as text_file:
            for line in text_file:
                things = line.split(':')
                if things[0] == name:
                    values.append(things[1])
                    values.append(things[2])
                    if not things[3] == "sub account is empty":
                        values.append(things[3])
        return values
