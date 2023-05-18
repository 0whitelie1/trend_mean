import pandas as pd
import numpy as np
from scipy.stats import linregress
import math
import matplotlib.pyplot as plt
import glob
import time


start_date = '2015-1-1'

def calculate_angle(stock):
    data = pd.read_csv("./data/yahoo/"+stock+".csv", delimiter=',')
    data = data.dropna(how='any',axis=0) # BAZI DATALAR NULL onları yoktmek

    data0 = data.copy()
    data0['Date'] = pd.to_datetime(data0['Date'], errors='coerce')

    # date filter
    data0 = data0[data0.Date > start_date]

    data0['date_id'] = ((data0['Date'] - data0['Date'].min())).astype('timedelta64[D]')
    data0['date_id'] = data0['date_id'] + 1

    # low trend line

    data1 = data0.copy()
    data1['Adj Close'] = data1['Adj Close'].astype(np.float64)
   
    reg = linregress(
                        x=data1['date_id'],
                        y=data1['Adj Close'],
                        )



    data0['low_trend'] = reg[0] * data0['date_id'] + reg[1]

    trend_low_min_index = data0[['low_trend']].idxmin()
    trend_low_max_index = data0[['low_trend']].idxmax()

    trend_low_min_index_value = trend_low_min_index[0]
    trend_low_max_index_value = trend_low_max_index[0]


    trend_low_min_value = data0["low_trend"][trend_low_min_index_value]
    trend_low_max_value = data0["low_trend"][trend_low_max_index_value]
    
    deltaX = data0["date_id"][trend_low_max_index_value] - data0["date_id"][trend_low_min_index_value]
    deltaY = data0["Adj Close"][trend_low_max_index_value] - data0["Adj Close"][trend_low_min_index_value]

    trend_low_angle = math.degrees(math.atan((deltaY) / deltaX))

    change = data0["Adj Close"][trend_low_max_index_value] / data0["Adj Close"][trend_low_min_index_value]

   

    return stock, data0["Adj Close"][trend_low_min_index_value], data0["Adj Close"][trend_low_max_index_value], deltaX, trend_low_angle, change

##########################################################################################################################

def plot(stock, rating):
    data = pd.read_csv("./data/yahoo_price/" + stock + ".csv", delimiter=',')
    data = data.dropna(how='any', axis=0)  # BAZI DATALAR NULL onları yoktmek

    data0 = data.copy()
    data0['Date'] = pd.to_datetime(data0['Date'], errors='coerce')

    # date filter
    data0 = data0[data0.Date > start_date]

    data0['date_id'] = ((data0['Date'] - data0['Date'].min())).astype('timedelta64[D]')
    data0['date_id'] = data0['date_id'] + 1

    # low trend line

    data1 = data0.copy()
    data1['Adj Close'] = data1['Adj Close'].astype(np.float64)
    # print(data1.dtypes)
    # exit()

    reg = linregress(
        x=data1['date_id'],
        y=data1['Adj Close'],
    )

    data0['low_trend'] = reg[0] * data0['date_id'] + reg[1]

   
    plt.figure()
    plt.plot(data0['Date'], data0['Adj Close'], 'b', linestyle='-', markersize=1)
    plt.plot(data0['Date'], data0['low_trend'], 'g', linestyle='-', markersize=1)
    plt.xlabel('Date')
    plt.savefig('./output/mean/'+str(rating) + "." + stock + '.png')
    # plt.show()

########################################################################################################################

df_output = pd.DataFrame(columns=['Stock', "trend_low_min", "trend_low_max", "trend_low_count", 'trend_low_angle', 'change_percentage'])

path = './data/yahoo/'
files = [f for f in glob.glob(path + "**/*.csv", recursive=True)]


counter = 0
for f in files:
    counter = counter + 1
    StockName = f.replace("./data/yahoo\\", "")
    StockName = StockName.replace('.csv', "")

    print(counter, "/", len(files), " -- ", StockName)

    try:
        stock, trend_low_min, trend_low_max, trend_low_count, trend_low_angle, change = calculate_angle(StockName)
    except:
        print("error: " + StockName)

    df_output = df_output.append({'Stock': stock,
                                  "trend_low_min": trend_low_min,
                                  "trend_low_max": trend_low_max,
                                  "trend_low_count": trend_low_count,
                                  'trend_low_angle': trend_low_angle,
                                  'change_percentage': change
                                  },
                                 ignore_index=True)






# sorting
df_output_sort = df_output.sort_values(by=['change_percentage'], ascending= False)

df_output_sort.to_csv("./output/low_trend_" + time.strftime("%Y%m%d-%H%M%S") + ".csv", sep='\t', encoding='utf-8')

pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', 10)

print(df_output_sort.head(20))


for i in range(20):
    plot(df_output_sort.iloc[i, 0], i)
