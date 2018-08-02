# Alpha vantage API: EY2QBMV6MD9FX9CP
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import time
import datetime
import argparse


class Tracker:
    def __init__(self):
        self.ALPHA_VANTAGE_KEY = 'EY2QBMV6MD9FX9CP'
        self.TODAY = datetime.datetime.today()
        self.WAGO_DT = 7
        self.MAGO_DT = 28
        self.ts = TimeSeries(key=self.ALPHA_VANTAGE_KEY)

        self.stocks = None
        self.period = None
        self.opens = None
        self.currents = {}
        return

    def read_stocks(self, stockfile):
        """
        Specify stocks to track via an input file.
        Expected to be upgraded to hit a majority of S&P stocks or industries in future

        :param stockfile: file with new line separated stock tickers to track
        :return: Nothing
        """

        with open(stockfile, 'r') as f:
            stocks = [line.strip() for line in f]

        stocks = [x for x in stocks if x]  # In case there's an extra blank space

        self.stocks = stocks
        return

    def specify_stocks(self, list_of_stocks):
        """
        Input specific stocks to check instead of going fromt he list

        :param list_of_stocks: List of str tickers
        :return: Nothing
        """
        self.stocks = list_of_stocks
        return

    def set_update_period(self, period):
        """
        Set the interval with which to update stock prices.
        Note that alpha_vantage has some issues with rapid stock grabbing. Over 1 min should be plenty

        :param period: Period between updates, in seconds
        :return: N/A
        """
        self.period = period
        return

    def get_date_days_ago(self, dt):
        """
        Get the date a certain number of days ago

        :param dt: Days difference, in number of days
        :return: Historical Date as a string
        """
        return str(self.TODAY - datetime.timedelta(dt)).split()[0]

    def grab_av_stock_data(self, fun, s):
        """
        Continuously attempt to grab alpha_vantage stock data
        Time delay of 10 seconds if we over-ping
        outputsize flag allows us to only get last 100 days

        fun lets us use this same function for batch quotes and opens

        :param fun: Function to ping alpha vantage with
        :param s: stock to get
        :return: daily opens for a stock for last 100 days
        """

        successful_grab = False
        stock_data = None

        while successful_grab is not True:
            try:
                if fun == 'opens':
                    stock_data, _ = self.ts.get_daily_adjusted(s, outputsize='compact')
                elif fun == 'quotes':
                    stock_data, _ = self.ts.get_batch_stock_quotes(symbols=self.stocks)
                else:
                    print("Function Not Valid")
                    return
                successful_grab = True
            except ValueError:
                print('Sleeping for 10')
                time.sleep(10)

        return stock_data

    def get_opens(self):
        """
        Get the opens from today, a week ago (WAGO) and a month ago (MAGO) for stocks
        If today, month or week ago was a holiday or weekend, look at the nearest earlier date with data
        This might shit itself on weekends
        Store as self.opens for bugfixing and checking later

        :return: nx3 DataFrame, n is number of stocks to look at
        """

        opens = pd.DataFrame(index=self.stocks, columns=['Today', 'WAGO', 'MAGO'])

        for s in self.stocks:
            print('Collecting {} data'.format(s))

            daily_opens = self.grab_av_stock_data('opens', s)
            three_opens = []

            for days_ago in [0, self.WAGO_DT, self.MAGO_DT]:
                date = self.get_date_days_ago(days_ago)

                while date not in daily_opens:
                    days_ago += 1
                    date = self.get_date_days_ago(days_ago)

                open_price = float(daily_opens[date]['1. open'])
                three_opens.append(open_price)

            opens.loc[s, :] = three_opens

            time.sleep(1)  # AlphaVantage don't hate me

        self.opens = opens
        return opens

    def get_currents(self):
        """
        Get current quotes from stocks and store with a time index

        :return: nx3 DataFrame with current price as all three columns per stock
        """

        currents = pd.DataFrame(index=self.stocks,
                                columns=['Today', 'WAGO', 'MAGO'],
                                dtype=float)

        data = self.grab_av_stock_data('quotes', None)
        price_quotes = [(s['1. symbol'], float(s['2. price'])) for s in data]

        for (a, b) in price_quotes:
            currents.loc[a, :] = b

        # Store all the calls within the object, for looking at later
        self.store_currents(currents['Today'])

        return currents

    def generate_block_update(self, opens, currents):
        """
        Create a single update df with changes and opens for today, MAGO, WAGO, and current quote

        :param opens: dataframe of open prices for stocks, from get_opens
        :param currents: Current stock prices, outputted from get_currents
        :return: nx7 df with Changes (x3), Current, Opens (x3)
        """
        change = ((currents / opens) - 1) * 100

        update = pd.concat([change, currents['Today'], self.opens], axis=1)
        update.columns = ['Today_Chg',
                          'WAGO_Chg',
                          'MAGO_Chg',
                          'Current',
                          'Today_Open',
                          'WAGO_Open',
                          'MAGO_Open']

        return update

    def store_currents(self, current_prices):
        """
        Every time current prices are called, store them
        This is for future debugging and evaluating purposes

        :param current_prices: df of current prices
        :return: N/A
        """
        time_now = datetime.datetime.now().time()
        self.currents[time_now] = current_prices
        return

    def run(self):
        """
        Run the entire stock tracking system
        :return:
        """
        opens = self.get_opens()

        while True:
            currents = self.get_currents()
            update = self.generate_block_update(opens, currents)

            print(update)
            print('\n')
            time.sleep(self.period)


if __name__ == "__main__":
    """
    Run by python3 -m StockTracker.StockTracker --stocks NTAP GOOG IBM etc. etc.
    & at end of command to run in background
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--stocks',
                        nargs="*",
                        type=str,
                        default=None)

    parser.add_argument('--period',
                        nargs="*",
                        type=int,
                        default=20)

    parser.add_argument('--textonly', dest='textonly', action='store_true')
    parser.set_defaults(textonly=True)

    args = parser.parse_args()

    tracker = Tracker()
    tracker.set_update_period(args.period)

    if args.stocks is not None:
        tracker.specify_stocks(args.stocks)
    else:
        tracker.read_stocks('StockTracker/stocks')

    if args.textonly:
        tracker.run()
    else:
        from StockTracker.StockHUD import StockHUD
        shud = StockHUD(tracker)
        shud.run_tracker()

