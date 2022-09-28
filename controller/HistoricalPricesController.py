import csv
import os
import pathlib
from model.MarketData import MarketData
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor


class HistoricalPricesController:
    """ Orders csv files and fetches historical prices of coins. For each time_frame and coin all candles of the last
     year are stored in results/Historical Prices"""
    def __init__(self):
        self.account = None
        self.PATH_OF_THIS_FILE = pathlib.Path(__file__)
        self.PATH_TO_RESULTS = pathlib.Path(__file__).parent.joinpath('results')
        self.PATH_TO_PRICES = pathlib.Path(__file__).parent.joinpath('results').joinpath('Historical Prices')
        self.PATH_TO_TESTS = pathlib.Path(__file__).parent.joinpath('results').joinpath('Backtest')

    def set_account(self, account):
        self.account = account

    def write_data(self, coin, time_frame):
        """ if a file with this coin and time_frame exists it gets appended until now. If it does not
         exist it gets created and all market data out of this time:frame for the last year are loaded """
        # file is empty
        if not self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv').is_file():
            # time, timestamp, open, high, low, close, volume
            self.make_last_year_file(coin, time_frame)
        else:
            timestamp_last_row = self.get_timestamp_of_last_row(coin, time_frame)
            next_timestamp = self.next_timestamp_after_last_row(timestamp_last_row, time_frame)
            now = self.timestamp_now_minus_time_frame(time_frame)
            self.append_file_by_lines_between_last_line_and_now(coin, next_timestamp, now, time_frame)
        self.cut_first_rows(coin, time_frame)

    @staticmethod
    def next_timestamp_after_last_row(timestamp_last_row, time_frame):
        """ calculates the offset to the next candle interval which is to be fetched """
        if time_frame == "1min":
            return timestamp_last_row + 60
        if time_frame == "5min":
            return timestamp_last_row + 60 * 5
        if time_frame == "15min":
            return timestamp_last_row + 60 * 15
        if time_frame == "1h":
            return timestamp_last_row + 60 * 60
        if time_frame == "4h":
            return timestamp_last_row + 60 * 240
        if time_frame == "1day":
            return timestamp_last_row + 60 * 1440

    @staticmethod
    def get_extra_offset(time_frame):
        """ return this time_frame in minutes """
        if time_frame == "1min":
            return 1
        if time_frame == "5min":
            return 5
        if time_frame == "15min":
            return 15
        if time_frame == "1h":
            return 60
        if time_frame == "4h":
            return 240
        if time_frame == "1day":
            return 1440

    @staticmethod
    def timestamp_now_minus_time_frame(time_frame):
        """ returns a timestamp time_frame time earlier from now  """
        if time_frame == "1min":
            return int(datetime.now().timestamp()) - 60
        if time_frame == "5min":
            return int(datetime.now().timestamp()) - 60 * 5
        if time_frame == "15min":
            return int(datetime.now().timestamp()) - 60 * 15
        if time_frame == "1h":
            return int(datetime.now().timestamp()) - 60 * 60
        if time_frame == "4h":
            return int(datetime.now().timestamp()) - 60 * 240
        if time_frame == "1day":
            return int(datetime.now().timestamp()) - 60 * 1440

    def append_file_by_lines_between_last_line_and_now(self, coin, next_timestamp, now, time_frame):
        """ appends the csv file by all missing candles until now. next_timestamp is the next time to get after
         the last candle in the csv file. While the next_timestamp is smaller than now. All candles in this period
         are catched. otherwise the missing candles are catched"""
        pair = coin + "-PERP"
        m = MarketData()
        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "a", newline='') as fp:
            while True:
                if next_timestamp + 60 * 1440 * self.get_extra_offset(time_frame) < now:
                    next_day = next_timestamp + 60 * 1440 * self.get_extra_offset(time_frame)
                    candles_of_this_day = m.get_candles_time(pair, 60 * self.get_extra_offset(time_frame),
                                                             next_timestamp, next_day)
                    candle_list = []
                    for c in candles_of_this_day:
                        candle_list.append(self.make_time_and_stamp(c))
                    writer = csv.writer(fp, delimiter=",")
                    writer.writerows(candle_list)
                    next_timestamp = next_day
                else:
                    candles_of_this_day = m.get_candles_time(pair, 60 * self.get_extra_offset(time_frame),
                                                             next_timestamp, now)
                    candle_list = []
                    for c in candles_of_this_day:
                        candle_list.append(self.make_time_and_stamp(c))
                    writer = csv.writer(fp, delimiter=",")
                    writer.writerows(candle_list)
                    break

    def make_last_year_file(self, coin, time_frame):
        """ makes a csv file with all candles in this time_frame of this coin for the last year """
        pair = coin + "-PERP"
        m = MarketData()
        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "a", newline='') as fp:
            timestamps_of_last_365_days = []

            for i in range(366):
                time = datetime.now() - timedelta(minutes=1440 * i)
                timestamps_of_last_365_days.append(time.timestamp())

            timestamps_of_last_365_days.reverse()
            candles = self.get_candles(m, pair, time_frame, timestamps_of_last_365_days)
            candle_list = []
            for c in candles:
                candle_list.append(self.make_time_and_stamp(c))
            # candles need to be ordered because they are fetched with Threads simultaneously
            self.order_list(candle_list)
            writer = csv.writer(fp, delimiter=",")
            writer.writerows(candle_list)

    @staticmethod
    def order_list(list_to_order):
        """ orders this list by its first element (the timestamp of this candle) """
        list_to_order.sort(key=lambda x: float(x[1]))

    @staticmethod
    def get_candles(m, pair, time_frame, timestamps_of_last_365_days):
        """ catches all candles. if max_workers is too high the exchanges gives an Error: slow down.
         The different intervals are chosen so that there are as few api calls as possible. The max number of
          candles per api call is 1500. So at the 1min frame for example 365 api calls are sent because
          60min * 24h per day = 1440 min per day. And 1440 < 1500. And you need all 365 days """
        candles = []

        def get_candles1min(index):
            candles.extend(m.get_candles_time(pair, 60, timestamps_of_last_365_days[index],
                           timestamps_of_last_365_days[index + 1]))
        if time_frame == "1min":
            with ThreadPoolExecutor(max_workers=20) as executor:
                for i in range(365):
                    executor.submit(get_candles1min, i)

        def get_candles5min(index):
            candles.extend(m.get_candles_time(pair, 300, timestamps_of_last_365_days[index*5],
                           timestamps_of_last_365_days[(index + 1)*5]))
        if time_frame == "5min":
            with ThreadPoolExecutor(max_workers=20) as executor:
                for i in range(73):
                    executor.submit(get_candles5min, i)

        def get_candles15min(index):
            candles.extend(m.get_candles_time(pair, 900, timestamps_of_last_365_days[index*15],
                           timestamps_of_last_365_days[(index + 1)*15]))
        if time_frame == "15min":
            with ThreadPoolExecutor(max_workers=20) as executor:
                for i in range(24):
                    executor.submit(get_candles15min, i)
            candles.extend(m.get_candles_time(pair, 900, timestamps_of_last_365_days[361],
                           timestamps_of_last_365_days[365]))

        def get_candles1h(index):
            candles.extend(m.get_candles_time(pair, 3600, timestamps_of_last_365_days[index * 60],
                           timestamps_of_last_365_days[(index + 1) * 60]))
        if time_frame == "1h":
            with ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(6):
                    executor.submit(get_candles1h, i)
            candles.extend(m.get_candles_time(pair, 3600, timestamps_of_last_365_days[361],
                           timestamps_of_last_365_days[365]))
        if time_frame == "4h":
            candles.extend(m.get_candles_time(pair, 14400, timestamps_of_last_365_days[0],
                           timestamps_of_last_365_days[182]))
            candles.extend(m.get_candles_time(pair, 14400, timestamps_of_last_365_days[183],
                           timestamps_of_last_365_days[365]))
        if time_frame == "1day":
            candles.extend(m.get_candles_time(pair, 86400, timestamps_of_last_365_days[0],
                           timestamps_of_last_365_days[365]))
        return candles

    def cut_first_rows(self, coin, time_frame):
        """ all candles in the csv file which are older than one year are deleted """
        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "r") as file:
            data = file.readlines()
        last_row = data[-1].split(',')
        timestamp_last_row = last_row[1]
        timestamp_last_year = int(timestamp_last_row) - 365 * 24 * 60 * 60
        data_read = []
        for d in data:
            if int(d.split(',')[1]) <= timestamp_last_year:
                pass
            else:
                data_read.append(d)

        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "w", newline='') as fp:
            fp.writelines(data_read)

    def delete_file(self, file_name):
        try:
            os.remove(self.PATH_TO_TESTS.joinpath(file_name + '.csv'))
        except OSError:
            pass

    def get_timestamp_of_last_row(self, coin, time_frame):
        """ returns the timestamp of the last row of the csv file with this coin and time_frame """
        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "r") as file:
            data = file.readlines()
        last_row = data[-1].split(',')
        return int(last_row[1])

    @staticmethod
    def unix_timestamp_to_time(time):
        return str(datetime.utcfromtimestamp(time))

    def make_time_and_stamp(self, list1):
        """ cuts unnecessary  data from the received candles"""
        list1 = list(list1.values())
        list1[1] = int(list1[1] / 1000)
        list1[0] = self.unix_timestamp_to_time(list1[1])
        return list1

    @staticmethod
    def time_to_unix_timestamp(time):
        return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_time_one_year_ago():
        return datetime.now() - timedelta(days=365)

    @staticmethod
    def get_time_n_days_ago(days):
        return datetime.now() - timedelta(days=int(days))

    def get_timestamp_n_days_ago(self, coin, days, time_frame):
        timestamp = self.get_timestamp_of_last_row(coin, time_frame)
        return timestamp - int(days) * 24 * 60 * 60

    @staticmethod
    def get_daytime_now():
        return datetime.now()

    def read_data(self, coin, time_frame, days):
        """ reads the csv file with this coin and time_frame. keeps only the last n days """
        time_n_days_ago = self.get_timestamp_n_days_ago(coin, days, time_frame)
        with open(self.PATH_TO_PRICES.joinpath(coin + time_frame + '.csv'), "r") as file:
            data = file.readlines()
            data_read = []
            for d in data:
                if int(d.split(',')[1]) <= time_n_days_ago:
                    pass
                else:
                    data_read.append(d.split(','))
        return data_read

    def make_backtest_file(self, strategy):
        """ writes the result of the backtest in a csv file with a name which the user has selected in the GUI """
        with open(self.PATH_TO_TESTS.joinpath(strategy.file_name + '.csv'), "a", newline='') as fp:
            writer = csv.writer(fp, delimiter=",")
            writer.writerow(strategy.header_list)
            writer.writerows(strategy.trades)

    def order_backtest_file(self, file_name, header_list, data):
        data.sort(reverse=True, key=lambda x: float(x[len(header_list)-1]))

        with open(self.PATH_TO_TESTS.joinpath(file_name + '.csv'), "w", newline='') as fp:
            writer = csv.writer(fp, delimiter=",")
            writer.writerow(header_list)
            writer.writerows(data)
