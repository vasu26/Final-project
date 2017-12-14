import pandas as pd
import pandas_datareader as web
import datetime as dt
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
        self.prices = None
        self.currency = None

    @staticmethod
    def user_input():

        selected_currency = input("\nPlease choose a base currency for the bitcoin from the following list:"
                                  "\n USD\n INR\n EUR\n(Type 'exit' to exit the program) Your Choice:")

        if selected_currency.upper() == 'USD':
            currency = 'BTC-USD'
        elif selected_currency.upper() == 'INR':
            currency = 'BTC-INR'
        elif selected_currency.upper() == 'EUR':
            currency = 'BTC-EUR'
        elif selected_currency.upper() == 'EXIT':
            print('\nExiting the program. Goodbye!')
            sys.exit()
        else:
            print('\nSorry, invalid input! Please try again\n')
            Bitvary.user_input()
        return currency

    def load_data(self):
        start_date = dt.datetime(2017, 1, 3)
        end_date = dt.datetime(2017, 11, 20)
        print('Extracting Dataset for BITCOIN in ', self.currency.split('-')[1])
        while self.prices is None:
            try:
                self.prices = web.DataReader(self.currency, 'yahoo', start_date, end_date)[['Open','Close']]
            except RemoteDataError:
                print("Still trying...\n")
                pass
            except req.ConnectionError:
                raise LoadDataException('Unable to download BITCOIN Dataset due to internect connectivity issues')

    def simulation_1(self):
            returns=self.prices['Close'].pct_change()
            last_price=self.prices['Close'][-1]

            num_simulations=1000 #Number of simulations
            days=252 #Number of working days in a year

            sim_df=pd.DataFrame()
            for x in range(num_simulations):
                count=0
                daily_volatility=returns.std()
                price_series=[]
                price=last_price*(1+np.random.normal(0,daily_volatility))
                price_series.append(price)

                for y in range(days):
                    if count==252:
                        break
                    price=price_series[count]*(1+np.random.normal(0,daily_volatility))
                    price_series.append(price)
                    count+=1

                sim_df[x]=price_series

            self.create_figure(sim_df)

    def simulation_2(self):
        days = 252  # Number of working days in a year
        returns = np.log(self.prices['Close'] / self.prices['Open'])
        daily_volatility = np.std(returns)
        annual_volatility = daily_volatility * ((days) ** (1 / 2))
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
        fig.suptitle('Frequencies of expected price occurences')
        n, bins, patches = plt.hist(scores, 100, normed=1, facecolor='green', alpha=0.5)
        # Adding a 'best fit' line
        y = mlab.normpdf(bins, np.median(scores), np.std(scores))
        plt.plot(bins, y, 'r--')
        plt.xlabel('Price')
        plt.ylabel('Frequency')
        print('Please open the "Price v/s Frequency" item from your taskbar for frequency of Prices')
        plt.show()

    def create_figure(self, sim_df):
        fig = plt.figure()
        fig.suptitle('Monte Carlo Simulation for predicting the value of BITCOINS in ' + self.currency.split('-')[1])
        plt.plot(sim_df)
        plt.axhline(y=self.prices['Close'][-1], color='r', linestyle='-')
        plt.xlabel('Day')
        plt.ylabel('Price')
        print('Please open the "Time v/s Price" item from your taskbar for a graphical view of the simulation')
        plt.show()


class LoadDataException(Exception):
    pass


if __name__ == "__main__":

    while True:
        bitvary = Bitvary()
        bitvary.currency = Bitvary.user_input()
        try:
            bitvary.load_data()
            print('Extraction successful! Running the simulation...')
            bitvary.simulation_2() # Change this to simulation_1 or simulation_2 to run the other solution
            retry = input('Would you like to run another simulation? (Y or N): ')
            if retry.upper() == 'Y':
                continue
            else:
                break
        except LoadDataException as lde:
            print(lde)
            break
    print('Exiting the program. Goodbye!')

