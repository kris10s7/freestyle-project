# app/robo_advisor.py

import csv
import requests
import json 
import os
import time
from dotenv import load_dotenv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly 
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as py_offline

load_dotenv()

def to_usd(my_price):
    return "${0:,.2f}".format(my_price)

#
#INFO INPUTS
#
# plotly.tools.set_credentials_file(username='sz745', api_key='5Bxn6nSI89uyyAkcjmKL')

api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
#print(api_key)

try:
    symbol = input("Please specify a stock symbol (e.g. MSFT) and press enter: ")

    if not symbol.isalpha():
            print("Oh, expecting a properly-formed stock symbol like 'MSFT'. Please try again.")
            exit()
# used isalpha() to check for alphabetical input only: https://www.geeksforgeeks.org/python-string-isalpha-application/

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(request_url)
    parsed_response = json.loads(response.text)  # parse json into a dictionary
    last_refreshed = parsed_response["Meta Data"]["3. Last Refreshed"]

# print(type(response))  #this is a Response
# print(response.status_code)  #200
# print(response.text)

except KeyError:
    print("Sorry, couldn't find any trading data for that stock symbol. Please try again.")
    exit()
# used Key Error exception handling outlined here: https://python101.pythonlibrary.org/chapter7_exception_handling.html

## Requesting daily data

tsd = parsed_response["Time Series (Daily)"]
dates = list(tsd.keys())
latest_day = dates[0] #assume first day is top; to do: sort to ensure latest day is first
latest_close = tsd[latest_day]["4. close"]


# get high price from each day
# high_prices = [10, 20, 30, 5] # maximum of all high prices
# recent_high = max(high_prices)

high_prices = []
low_prices = []

for date in dates:
    high_price = tsd[latest_day]["2. high"]
    low_price = tsd[latest_day]["3. low"]
    high_prices.append(float(high_price))
    low_prices.append(float(low_price))

recent_high = max(high_prices)
recent_low = min(low_prices)

#
# INFO OUTPUTS
#

# csv_file_path = "data/prices.csv"
csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")

csv_headers = ["timestamp", "open", "high", "low", "close", "volume"]

with open(csv_file_path, "w") as csv_file: # "w" means "open the file for writing"
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader() # uses fieldnames set above
    for date in dates:
        daily_prices = tsd[date]
        writer.writerow({
            "timestamp": date,
            "open": daily_prices["1. open"],
            "high": daily_prices["2. high"],
            "low": daily_prices["3. low"],
            "close": daily_prices["4. close"],
            "volume": daily_prices["5. volume"],
            })

print("-------------------------")
print(f"SELECTED SYMBOL: {symbol}")

print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")

now = time.strftime("%Y-%m-%d %H:%M:%p")
# used code to format date and time suggested in this stackoverflow thread: https://stackoverflow.com/questions/31955761/converting-python-string-to-datetime-obj-with-am-pm
print("REQUEST AT: " + str(now))
print("-------------------------")

print(f"LATEST DAY: {last_refreshed}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")

print("-------------------------")
if float(latest_close) <= recent_low:
    print("RECOMMENDATION: BUY!")
    print(f"RECOMMENDATION REASON: {symbol}'s latest closing price is less than recent low")
else:
    print("RECOMMENDATION: DON'T BUY!")
    print(f"RECOMMENDATION REASON: {symbol}'s latest closing price is greater than its recent low")
print("-------------------------")
print(f"WRITING DATA TO CSV: {csv_file_path}")
print("-------------------------")
print("STATISTICS:")

# read prices.csv and set as pandas dataframe

csv_filepath = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")
df = pd.read_csv(csv_filepath, header=0)

# if we want to run stats on all columns
stock_statistics = df.describe()
print(stock_statistics)
print("-------------------------")

# if we want to customize which columns to run stats on
# open_close_stats = df[['open', 'close']]
# print(open_close_stats.describe())

# chart closing price
##y=df["timestamp"]
#x=df["close"]
#plt.plot(y, x)
#
#plt.title(f"{symbol}'s Closing Price")
#plt.xlabel("Date")
#plt.ylabel("Price")
#
#plt.show()
#
# candlestick chart using plotly offline

trace = go.Candlestick(x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])
data = [trace]

layout = go.Layout(
    title=go.layout.Title(
        text=f'{symbol} Candlestick Chart as of ' + str(last_refreshed),
        xref='paper',
        x=0
    ),
)

fig = go.Figure(data=data, layout=layout)
candlestick_filepath = os.path.join(os.path.dirname(__file__), "..", "chart", "candlestick.html")
plotly.offline.plot(fig, filename='candlestick.html')

print(f"SUCCESSFULLY GENERATED CANDLESTICK CHART ({candlestick_filepath}) AND SECTOR PERFORMANCE CHART :)")
print("-------------------------")

api_key = os.environ.get("ALPHAVANTAGE_API_KEY")

request_url = f"https://www.alphavantage.co/query?function=SECTOR&apikey={api_key}"
response = requests.get(request_url)
parsed_response = json.loads(response.text)  # parse json into a dictionary
last_refreshed = parsed_response["Meta Data"]["Last Refreshed"]

##Retrieving sector data

one_day = parsed_response["Rank B: 1 Day Performance"]
one_month = parsed_response["Rank D: 1 Month Performance"]
three_month = parsed_response["Rank E: 3 Month Performance"]
YTD = parsed_response["Rank F: Year-to-Date (YTD) Performance"]

## removing the "%" and creating new dictionaries
w = one_day.values()
w = [s.strip('%') for s in w]
one_day_dict = dict(zip(one_day.keys(),map(float,w))) 
  
x = one_month.values()
x = [s.strip('%') for s in x]
one_month_dict = dict(zip(one_month.keys(),map(float,x)))

y = three_month.values()
y = [s.strip('%') for s in y]
three_month_dict = dict(zip(three_month.keys(),map(float,y)))

z = YTD.values()
z = [s.strip('%') for s in z]
YTD_dict = dict(zip(YTD.keys(),map(float,z)))

  # How to remove a character from a list of strings: https://stackoverflow.com/questions/8282553/removing-character-in-list-of-strings
  # How to remove convert two lists into a dictionary: https://therenegadecoder.com/code/how-to-convert-two-lists-into-a-dictionary-in-python/
  # How to converting list of strings to float: https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats

##creating performance chart for all sectors

trace1 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Communication Services"], one_month_dict["Communication Services"], three_month_dict["Communication Services"], YTD["Communication Services"]],
    name='Communication Services',
    marker=dict(
        color='rgb(102, 178, 255)' #website used to find color codes: https://www.rapidtables.com/web/color/RGB_Color.html
    )
)
trace2 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Consumer Discretionary"], one_month_dict["Consumer Discretionary"], three_month_dict["Consumer Discretionary"], YTD_dict["Consumer Discretionary"]],
    name='Consumer Discretionary',
    marker=dict(
        color='rgb(127, 0, 255)'
    )
)

trace3 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Consumer Staples"], one_month_dict["Consumer Staples"], three_month_dict["Consumer Staples"], YTD_dict["Consumer Staples"]],
    name='Consumer Staples',
    marker=dict(
        color='rgb(255, 153, 255)'
    )
)

trace4 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Financials"], one_month_dict["Financials"], three_month_dict["Financials"], YTD_dict["Financials"]],
    name='Financials',
    marker=dict(
        color='rgb(0, 255, 128)'
    )
)

trace5 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Energy"], one_month_dict["Energy"], three_month_dict["Energy"], YTD_dict["Energy"]],
    name='Energy',
    marker=dict(
        color='rgb(255, 0, 0)'
    )
)

trace6 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Health Care"], one_month_dict["Health Care"], three_month_dict["Health Care"], YTD_dict["Health Care"]],
    name='Health Care',
    marker=dict(
        color='rgb(241, 255, 28)'
    )
)

trace7 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Industrials"], one_month_dict["Industrials"], three_month_dict["Industrials"], YTD_dict["Industrials"]],
    name='Industrials',
    marker=dict(
        color='rgb(192, 192, 192)'
    )
)

trace8 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Information Technology"], one_month_dict["Information Technology"], three_month_dict["Information Technology"], YTD_dict["Information Technology"]],
    name='Information Technology',
    marker=dict(
        color='rgb(62, 17, 239)'
    )
)

trace9 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Materials"], one_month_dict["Materials"], three_month_dict["Materials"], YTD_dict["Materials"]],
    name='Materials',
    marker=dict(
        color='rgb(255, 153, 51)'
    )
)

trace10 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Real Estate"], one_month_dict["Real Estate"], three_month_dict["Real Estate"], YTD_dict["Real Estate"]],
    name='Real Estate',
    marker=dict(
        color='rgb(26, 118, 255)'
    )
)

trace11 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_dict["Utilities"], one_month_dict["Utilities"], three_month_dict["Utilities"], YTD_dict["Utilities"]],
    name='Utilities',
    marker=dict(
        color='rgb(96, 96, 96)'
    )
)


data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8, trace9, trace10, trace11]
layout = go.Layout(
    title='Sector Performance Chart as of '+ str(last_refreshed),
    xaxis=dict(
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    yaxis=dict(
        title='Performance (%)',
        titlefont=dict(
            size=16,
            color='rgb(107, 107, 107)'
        ),
        tickfont=dict(
            size=14,
            color='rgb(107, 107, 107)'
        )
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1
)

fig = go.Figure(data=data, layout=layout)
sector_chart_filepath = os.path.join(os.path.dirname(__file__), "..", "chart", "sector_chart.html")
plotly.offline.plot(fig, filename='sector_chart.html')

