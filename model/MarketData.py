from model.FTX_Class import FtxClient
from datetime import datetime, timedelta
import pandas as pd
import collections


class MarketData:
    """ Gets market datas can be used without an FTX Account """
    def __init__(self):
        self.client = FtxClient()

    def get_candles(self, pair, candle_interval, minutes):
        """ returns all candles in this interval
        :param pair: the market to get the candles from
        :param candle_interval: window length in seconds. options: 15, 60, 300, 900, 3600, 14400, 86400,
        or any multiple of 86400 up to 30*86400
        :param minutes: all candles in this timeframe """
        return self.client.get_historical_prices(pair, candle_interval, int(self.date_time_to_timestamp(minutes)[1]),
                                                 int(self.date_time_to_timestamp(minutes)[0]))

    def get_candles_time(self, pair, candle_interval, start_time, end_time):
        return self.client.get_historical_prices(pair, candle_interval, start_time, end_time)

    def get_trades(self, pair, minutes):
        return self.client.get_historical_trades(pair, self.date_time_to_timestamp(minutes)[1],
                                                 self.date_time_to_timestamp(minutes)[0])

    def get_trades_with_timestamp(self, pair, start_time, end_time):
        return self.client.get_historical_trades(pair, start_time, end_time)

    def get_trades_min(self, pair, start_time, end_time):
        return self.client.get_historical_trades(pair, start_time, end_time)

    @staticmethod
    def date_time_to_timestamp(minutes):
        """ calculates timestamp now and n minutes back """
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        last_hour_date_time = datetime.now() - timedelta(minutes=minutes)
        timestamp1 = datetime.timestamp(last_hour_date_time)
        return timestamp, timestamp1

    def get_candle_list(self, pair, interval, length):
        """ return all candles in this interval + 30 extra candles for rsi accuracy """
        candles = []
        candle_closes = []
        if interval == "1min":
            candles.extend(self.get_candles(pair, 60, (length * 5)))
        elif interval == "5min":
            candles.extend(self.get_candles(pair, 300, 5 * (length * 5)))
        elif interval == "15min":
            candles.extend(self.get_candles(pair, 900, 15 * (length * 5)))
        elif interval == "1h":
            candles.extend(self.get_candles(pair, 3600, 60 * (length * 5)))
        elif interval == "4h":
            candles.extend(self.get_candles(pair, 14400, 240 * (length * 5)))
        elif interval == "1day":
            candles.extend(self.get_candles(pair, 86400, 1440 * (length * 5)))
        for candle in candles:
            candle_closes.append(candle['close'])

        data = {"close": candle_closes}
        df = pd.DataFrame(data)
        return df

    def get_candle_list1(self, pair, time_frame, length):
        """ returns all candles in this interval """
        if time_frame == "1min":
            return self.get_candles(pair, 60, 1 * length)
        elif time_frame == "5min":
            return self.get_candles(pair, 300, 5 * length)
        elif time_frame == "15min":
            return self.get_candles(pair, 900, 15 * length)
        elif time_frame == "1h":
            return self.get_candles(pair, 3600, 60 * length)
        elif time_frame == "4h":
            return self.get_candles(pair, 14400, 240 * length)
        elif time_frame == "1day":
            return self.get_candles(pair, 86400, 1440 * length)

    def get_current_ma(self, coin, time_frame, interval):
        """ calculates the ma of this coin in this time_frame """
        candles = self.get_candle_list1(self.create_pair(coin), time_frame, interval)
        close_sum = 0
        for c in candles:
            close = c['close']
            close_sum += close

        ma = close_sum / interval
        return ma

    @staticmethod
    def get_all_mas(data, length):
        """ calculates all ma's from the past market datas in data. The first length elements are NaN"""
        # data = h.read_data("ETH", "1min", int(365))
        ma = []
        sum_all_candles_of_current_interval = 0
        counter = 0
        values_of_all_candles_of_current_interval = collections.deque([])
        for candle in data:
            candle_close_price = float(candle[5])
            if counter < length:
                sum_all_candles_of_current_interval += candle_close_price
                values_of_all_candles_of_current_interval.append(candle_close_price)
                ma.append(None)
            else:
                first_element = values_of_all_candles_of_current_interval.popleft()
                sum_all_candles_of_current_interval -= first_element
                sum_all_candles_of_current_interval += candle_close_price
                ma_value = sum_all_candles_of_current_interval / length
                ma.append(ma_value)
                values_of_all_candles_of_current_interval.append(candle_close_price)
            counter += 1
        return ma

    """
    Title: RSI calculation to match Tradingview
    Author: Jmoz
    Date: 2019
    Availability: https://gist.github.com/jmoz/1f93b264650376131ed65875782df386
    """
    @staticmethod
    def get_rsi(ohlc: pd.DataFrame, period: int = 14) -> pd.Series:
        """ calculates all rsi from the data in DataFrame """
        delta = ohlc["close"].diff()

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

        rs = _gain / _loss
        return pd.Series(100 - (100 / (1 + rs)), name="RSI")

    def get_last_rsi_of_list(self, candles, period):
        rsi = self.get_rsi(candles, int(period))
        return rsi.iat[-1]

    def get_last_rsi(self, coin, time, length):
        pair = self.create_pair(coin)
        candle_list = self.get_candle_list(pair, time, int(length))
        rsi = self.get_rsi(candle_list, int(length))
        return rsi.iat[-1]

    def get_rsi_list(self, data, period: int = 14):
        rsi = self.get_rsi(data, period)
        return rsi

    def get_price(self, coin):
        """ returns the price of the coin """
        response = self.client.get_single_future(self.create_pair(coin))
        price = response['mark']
        return price

    @staticmethod
    def create_pair(coin):
        return coin + "-PERP"

    def get_markets(self):
        return self.client.list_markets()
