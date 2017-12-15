import pandas as pd
import pandas_datareader as web
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from pandas_datareader._utils import RemoteDataError
import requests.exceptions as req
import sys
import math
from scipy.stats import t
import matplotlib.mlab as mlab


style.use('ggplot')


class Bitvary:

    def __init__(self):
        """
        prices: the dataframe we are using to store the bitcoin prices for each currency
        currency: a string that stores the ticker for bitcoin data extraction. This keeps changing as per the user's choice
        """
        self.prices = None
        self.currency = None
        self.start_date = None
        self.end_date = None

    @staticmethod
    def user_input():
        """
        This function prompts the user for an input to choose a currency in which they would like to run the simulation
        :return: Returns the selected currency which becomes the ticker for data extraction from Yahoo
        selected_currency: a string that takes the user's input and checks if it matches any of the options we provide

        """
        selected_currency = input("\nPlease choose a base currency for the bitcoin from the following list:\n USD\n INR\n EUR\n Your Choice:")

        if selected_currency.upper() == 'USD':
            currency = 'BTC-USD'
        elif selected_currency.upper() == 'INR':
            currency = 'BTC-INR'
        elif selected_currency.upper() == 'EUR':
            currency = 'BTC-EUR'
        else:
            print('\nInvalid Input.\nExiting the program. Goodbye!')
            sys.exit()
        return currency

    def date_input_format(self):
        """
        :return:nothing
        sets the start and end month, day and year to be used by the load_data function
        """

        start_date_string = input('Please enter the START DATE you would like to start the simulation from (Format: MM-DD-YYYY, please type the hyphens):')
        end_date_string = input('Please enter the END DATE you would like to run the simulation till (Format: MM-DD-YYYY, please type the hyphens):')
        try:
            self.start_date = datetime.strptime(start_date_string, '%m-%d-%Y')
            self.end_date = datetime.strptime(end_date_string, '%m-%d-%Y')
        except ValueError:
            raise LoadDataException("Oops! Invalid Date Format.")

    def load_data(self):
        """
        Based on user's input, this function loads the data pertaining to the selected currency into our dataframe
        :return: nothing
        start_date: uses the values set by date_input_format to set the start date
        end_date: uses the values set by date_input_format to set the end date
        """

        print('Extracting Dataset for BITCOIN in ', self.currency.split('-')[1])
        while self.prices is None:
            try:
                self.prices = web.DataReader(self.currency, 'yahoo', self.start_date, self.end_date)[['Open', 'Close']]
                print(self.prices)
            except RemoteDataError:
                print("Still trying...\n")
                pass
            except req.ConnectionError:
                raise LoadDataException('Unable to download BITCOIN Dataset due to internect connectivity issues')

    def simulation_v1(self):
        """
        This function prepares the first chart that we display with the result of running a 1000 simulations
        :return:nothing
        brings up the chart on the user's screen

        >>> bitvary = Bitvary()
        >>> np.random.seed(1)
        >>> bitvary.prices =  pd.DataFrame([{'Open': 963.380005, 'Close': 995.440002}, {'Open': 995.440002, 'Close': 1017.049988}, {'Open': 1017.049988, 'Close': 1033.300049}, {'Open': 1033.300049, 'Close': 1135.410034}], index=['01-01-2015','01-02-2015','01-03-2015','01-04-2015'])
        >>> bitvary.currency = 'BTC-USD'
        >>> bitvary.simulation_v1()
        Please open the "Figure 1" item from your taskbar for a graphical view of the simulation
        """
        returns = self.prices['Close'].pct_change()
        last_price = self.prices['Close'][-1]

        num_simulations = 1000                              # Number of simulations
        days = 252                                          # Number of working days in a year

        sim_df = pd.DataFrame()
        for x in range(num_simulations):
            count = 0
            daily_volatility = returns.std()
            price_series = []
            price = last_price*(1+np.random.normal(0, daily_volatility))
            price_series.append(price)

            for y in range(days):
                if count == 252:
                    break
                price = price_series[count]*(1+np.random.normal(0, daily_volatility))
                price_series.append(price)
                count += 1

            sim_df[x] = price_series

        self.create_figure(sim_df)

    def simulation_v2(self):
        """
        This function prepares a histogram of the expected frequencies of prices based on which we can predict a most likely price
        :return:nothing

        >>> bitvary = Bitvary()
        >>> np.random.seed(1)
        >>> bitvary.prices =  pd.DataFrame([{'Open': 963.380005, 'Close': 995.440002}, {'Open': 995.440002, 'Close': 1017.049988}, {'Open': 1017.049988, 'Close': 1033.300049}, {'Open': 1033.300049, 'Close': 1135.410034}], index=['01-01-2015','01-02-2015','01-03-2015','01-04-2015'])
        >>> bitvary.currency = 'BTC-USD'
        >>> bitvary.simulation_v2()
        Avg:3639426759.98
        Median:3229703029.47
        Min:581409678.937
        Max:13442105871.0
        Mean:3639426759.98
        Standard Deviation:1883957039.13
        Confidence Interval 95%: 3522518398.150671, 3756335121.801802
        Please open the "Figure 1" item from your taskbar for a graphical view of the simulation
        Please open the "Figure 1" item from your taskbar for frequency of Prices
        """
        days = 252  # Number of working days in a year
        returns = np.log(self.prices['Close'] / self.prices['Open'])
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * (days ** (1 / 2))
        daily_drift = np.average(returns)
        annual_drift = daily_drift * 365
        mean_drift = daily_drift - 0.5 * daily_volatility ** 2

        num_simulations = 1000  # Number of simulations

        sim_df = pd.DataFrame()
        scores = []

        for x in range(num_simulations):
            count = 0
            price_series = []
            last_price = self.prices['Close'][-1]
            score = last_price * math.e ** (
            (annual_drift - 0.5 * annual_volatility ** 2) + annual_volatility * np.random.normal(0, 1))
            scores.append(score)
            for y in range(days):
                if count == 252:
                    break
                log_return = mean_drift + (daily_volatility * np.random.normal(0, 1))
                price = last_price * (math.e ** log_return)
                price_series.append(price)
                last_price = price
                count += 1

            sim_df[x] = price_series

        b_std = np.std(scores)
        b_mean = np.mean(scores)
        # Calculating end values of 95% confidence interval
        end_vals = t.interval(0.95, len(scores) - 1)
        # Calculating Confidence interval
        conf_interval = [b_mean + conf * b_std / np.sqrt(len(scores)) for conf in end_vals]
        print("Avg:" + str(np.average(scores)))
        print("Median:" + str(np.median(scores)))
        print("Min:" + str(np.min(scores)))
        print("Max:" + str(np.max(scores)))
        print("Mean:" + str(b_mean))
        print("Standard Deviation:" + str(b_std))
        print("Confidence Interval 95%%: %f, %f" % (conf_interval[0], conf_interval[1]))

        self.create_figure(sim_df)

        Bitvary.create_histogram(scores)

    @staticmethod
    def create_histogram(scores):
        fig = plt.figure()
        fig.suptitle('Frequencies of expected price occurrences')
        n, bins, patches = plt.hist(scores, 100, normed=1, facecolor='green', alpha=0.5)
        # Adding a 'best fit' line
        y = mlab.normpdf(bins, np.median(scores), np.std(scores))
        plt.plot(bins, y, 'r--')
        plt.xlabel('Price')
        plt.ylabel('Frequency')
        print('Please open the "Figure 1" item from your taskbar for frequency of Prices')
        plt.show()

    def create_figure(self, sim_df):
        fig = plt.figure()
        fig.suptitle('Monte Carlo Simulation for predicting the value of BITCOINS in ' + self.currency.split('-')[1])
        plt.plot(sim_df)
        plt.axhline(y=self.prices['Close'][-1], color='r', linestyle='-')
        plt.xlabel('Day')
        plt.ylabel('Price')
        print('Please open the "Figure 1" item from your taskbar for a graphical view of the simulation')
        plt.show()


class LoadDataException(Exception):
    pass


if __name__ == "__main__":

    while True:
        bitvary = Bitvary()
        bitvary.currency = Bitvary.user_input()
        try:
            bitvary.date_input_format()
            bitvary.load_data()
            print('Extraction successful! Running the simulation...')
            bitvary.simulation_v2()            # Change this to simulation_v1 or simulation_v2 to run the other simulation version we developed
            retry = input('Would you like to run another simulation? (Y or N): ')
            if retry.upper() == 'Y':
                continue
            else:
                break
        except LoadDataException as lde:
            print(lde)
            break
    print('Exiting the program. Goodbye!')
