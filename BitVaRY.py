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
        '''
        prices: the dataframe we are using to store the bitcoin prices for each currency
        currency: a string that stores the ticker for bitcoin data extraction. This keeps changing as per the user's choice
        '''

        self.prices = None
        self.currency = None
        self.start_month=''
        self.end_month = ''
        self.start_day = ''
        self.end_day = ''
        self.start_year = ''
        self.end_year = ''

    @staticmethod
    def user_input():
        '''
        This function prompts the user for an input to choose a currency in which they would like to run the simulation
        :return: Returns the selected currency which becomes the ticker for data extraction from Yahoo
        selected_currency: a string that takes the user's input and checks if it matches any of the options we provide
        '''
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

    def date_input_format(self):
        '''
        :return:nothing
        sets the start and end month, day and year to be used by the load_data function
        '''

        st_dt=input('Please enter the START DATE you would like to start the simulation from (Format: MM-DD-YYYY, please type the hyphens):')
        en_dt = input('Please enter the END DATE you would like to run the simulation till (Format: MM-DD-YYYY, please type the hyphens):')
        self.start_month=int(st_dt.split('-')[0])
        self.start_day = int(st_dt.split('-')[1])
        self.start_year = int(st_dt.split('-')[2])
        self.end_month = int(en_dt.split('-')[0])
        self.end_day = int(en_dt.split('-')[1])
        self.end_year = int(en_dt.split('-')[2])

    def load_data(self):
        '''
        Based on user's input, this function loads the data pertaining to the selected currency into our dataframe
        :return: nothing
        start_date: uses the values set by date_input_format to set the start date
        end_date: uses the values set by date_input_format to set the end date
        '''
        #start_date = dt.datetime(2017, 1, 3)
        #end_date = dt.datetime(2017, 11, 20)

        self.date_input_format()
        start_date = dt.datetime(self.start_year, self.start_month, self.start_day)
        end_date = dt.datetime(self.end_year, self.end_month, self.end_day)
        print('Extracting Dataset for BITCOIN in ', self.currency.split('-')[1])
        while self.prices is None:
            try:
                self.prices = web.DataReader(self.currency, 'yahoo', start_date, end_date)[['Open','Close']]
            except RemoteDataError:
                print("Still trying...\n")
                pass
            except req.ConnectionError:
                raise LoadDataException('Unable to download BITCOIN Dataset due to internect connectivity issues')

    def simulations_1000_chart_maker(self):
        '''
        This function prepares the first chart that we display with the result of running a 1000 simulations
        :return:nothing
        brings up the chart on the user's screen
        '''
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
        '''
        This function prepares a histogram of the expected frequencies of prices based on which we can predict a most likely price
        :return:nothing
        '''
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