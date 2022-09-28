class UserInputController:
    """ Checks if the user inputs are ok. If not an Error message in this frame will be shown """
    def __init__(self):
        self.account = None

    def set_account(self, account):
        self.account = account

    @staticmethod
    def is_int(number):
        try:
            int(number)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_float(number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    def get_min_order_size(self, coin):
        return self.account.get_min_order_size(coin)

    def order_size_is_big_enough(self, frame, coin, dollar):
        """ checks if order_size is bigger then Minimum order size of the exchange """
        coin_price = self.get_price(coin)
        min_order_size = self.get_min_order_size(coin)
        order_size = float(dollar)/float(coin_price)
        min_order_size_in_dollar = round(coin_price * min_order_size, 2)
        if order_size < min_order_size:
            frame.show_error_massage("dollar is to small min order size: " + str(min_order_size) + " " + coin +
                                     "=(" + str(min_order_size_in_dollar) + "$)")
            return False
        return True

    def has_coin(self, coin):
        """ iterates over all coins and searches for the coin. If this coin is
         in this list return True"""
        coins = self.account.get_coin_list()
        for c in coins:
            if c == coin:
                return True
        return False

    def coin_exists(self, frame, coin):
        """ Checks if the coin exists on the exchange """
        if coin == "":
            frame.show_error_massage("coin is empty")
            return False
        coin = coin.strip()
        coin_exists = self.has_coin(coin)
        if not coin_exists:
            frame.show_error_massage(coin + " does not seem to exist")
            return False
        return True

    def coins_exists(self, frame, coins):
        """ Checks if the coins exists on the exchange """
        coins.strip()
        coins.replace(" ", "")
        coin_list = coins.split(",")
        for coin in coin_list:
            if not self.coin_exists(frame, coin):
                return False
        return True

    def time_frames_exists(self, frame, time_frames):
        """ Checks if the time frame exists """
        time_frames.strip()
        time_frames.replace(" ", "")
        time_frames_list = time_frames.split(",")
        for time_frame in time_frames_list:
            if not self.time_frame_exists(frame, time_frame):
                return False
        return True

    def get_price(self, coin):
        markets = self.account.get_all_markets()
        for c in markets:
            if c['name'] == coin + "-PERP":
                return c['price']

    @staticmethod
    def is_in_interval(frame, values):
        """ checks if the parameter at values[0] is in the interval of values[1](lower) and values[2](upper) """
        for key, value in values.items():
            if float(value[0]) < value[1] or float(value[0]) > value[2]:
                frame.show_error_massage(key + " must be between " + str(value[1]) + " and " + str(value[2]))
                return False
        return True

    @staticmethod
    def values_are_selected(frame, values):
        """ Checks if an account and an order type is selected """
        for key, value in values.items():
            if value == "Select an Option":
                frame.show_error_massage("Please select " + key)
                return False
        return True

    def is_a_int(self, frame, values):
        for key, value in values.items():
            if not self.is_int(value):
                frame.show_error_massage(key + " is not an integer")
                return False
        return True

    @staticmethod
    def time_frame_exists(frame, time_frame):
        time_frame = time_frame.strip()
        if not (time_frame == "1min" or time_frame == "5min" or time_frame == "15min" or time_frame == "1h"
                or time_frame == "4h" or time_frame == "1day"):
            frame.show_error_massage("time frame must be 1min, 5min, 15min, 1h, 4h or 1day")
            return False
        return True

    @staticmethod
    def file_name_exists(frame, file_name):
        if file_name == "":
            frame.show_error_massage("file name should not be empty")
            return False
        return True

    def trading_fees_are_ok(self, frame, fees):
        fees.strip()
        fees.replace(" ", "")
        fees_list = fees.split(",")
        boolean = True
        for fee in fees_list:
            if fee == "":
                frame.show_error_massage("trading fees is empty")
                return False
            if not self.is_float(fee):
                frame.show_error_massage(fee + " is not a number")
                return False
            if float(fee) < 0:
                frame.show_error_massage(fee + " must be greater then 0")
                return False
        return boolean

    def is_a_float(self, frame, values):
        for key, value in values.items():
            if not self.is_float(value):
                frame.show_error_massage(key + " is not a number")
                return False
        return True

    @staticmethod
    def enough_collateral(frame, dollar, collateral):
        if float(dollar) > collateral:
            frame.show_error_massage("dollar must be smaller then free collateral")
            return False
        return True

    @staticmethod
    def is_positive(frame, values):
        for key, value in values.items():
            if float(value) < 0:
                frame.show_error_massage(key + " must be greater then 0")
                return False
        return True

    @staticmethod
    def is_interval(frame, values):
        """ Checks if the lower upper and interval add up perfectly """
        for key, value in values.items():
            if (float(value[1]) - float(value[0])) % float(value[2]) != 0:
                # modulo with small values like 1.5%0.1 is not zero but 0.0999999.....
                if "0.0999999" not in str((float(value[1]) - float(value[0])) % float(value[2])):
                    frame.show_error_massage(value[2] + " of " + key + " does not add up with \n lower and upper")
                    return False
        return True

    @staticmethod
    def is_smaller(frame, values):
        """ Checks if first parameter in values(lower) is smaller than second parameter in values(upper)"""
        for value in values:
            if float(value[0]) > float(value[1]):
                frame.show_error_massage(value[2] + " must be smaller then " + value[3])
                return False
        return True

    @staticmethod
    def get_value_list(lower, upper, interval):
        """ returns a list with all values between lower and upper with a distance of interval between each value """
        value_list = []
        while True:
            if float(lower) > float(upper):
                break
            value_list.append(float(lower))
            lower = float(lower) + float(interval)
        return value_list

    def get_list(self, list_as_string):
        """ returns a list with all coins which are in the list list_as_string """
        back = []
        list_as_string = list_as_string.strip()
        list_as_string = list_as_string.replace(" ", "")
        value_list = list_as_string.split(",")
        for value in value_list:
            if self.is_float(value):
                back.append(float(value))
            else:
                back.append(value)
        return back
