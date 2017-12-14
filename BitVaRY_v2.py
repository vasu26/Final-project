import pandas as pd
import pandas_datareader as web
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from pandas_datareader._utils import RemoteDataError
import requests.exceptions as req

style.use('ggplot')

class bitvary:

    def readstore(choice):
        start = dt.datetime(2017, 1, 3)
        end = dt.datetime(2017, 11, 20)
        print('Extracting Dataset for BITCOIN in ', choice.split('-')[1])
        prices = web.DataReader(choice, 'yahoo', start, end)['Close']
        return prices

    def userinput(self):
        self.data_loaded = False
        self.exitflag = False
        currency = 'default'
        chosencurrency=input("Please choose a base currency for the bitcoin (Enter 1, 2, or 3. Press any other key to exit the program):\n1. USD\n2. INR\n3. EUR\nYour Choice:")
        if(chosencurrency == '1'):
            currency='BTC-USD'
        elif(chosencurrency=='2'):
            currency='BTC-INR'
        elif(chosencurrency=='3'):
            currency='BTC-EUR'
        else:
            self.exitflag=True
            
        if self.exitflag==True:
            print('Goodbye!')
        else:
            while not self.data_loaded:
                try:
                    if(currency=='default'):
                        self.exitflag=True
                        break
                    else:
                        prices=self.readstore(currency)
                        print('Extraction successful! Running the simulation...')
                        self.data_loaded=True
                        self.processing(prices,currency.split('-')[1],self)
                except RemoteDataError:
                    pass
                except req.ConnectionError as e:
                    print("Unable to download BITCOIN Dataset due to internect connectivity issues: ", e)
                    break

    def processing(prices,currency,self):
        if self.data_loaded==True:
            returns=prices.pct_change()
            last_price=prices[-1]
            #Number of simulations
            num_simulations=1000
            days=252 #number of working days in a year
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
            fig=plt.figure()
            fig.suptitle('Monte Carlo Simulation for predicting the value of BITCOINS in '+currency)
            plt.plot(sim_df)
            plt.axhline(y=last_price, color='r',linestyle='-')
            plt.xlabel('Day')
            plt.ylabel('Price')
            print('Please open the "Figure 1" item from your taskbar for a graphical view of the simulation')
            plt.show()
            retry=input('Would you like to run another simulation? (Y or N): ')
            if retry in ['y','Y']:
                print('\n\n')
                self.userinput(self)
            else:
                print('Goodbye!')
        else:
            if(self.exitflag==False):
                print("Sorry we were unable to load the data due to internet connectivity issues. Please check your internet connection and try again! The program will now terminate.")
            else:
                print('Exiting the program now. Goodbye!')

bitvary.userinput(bitvary)

