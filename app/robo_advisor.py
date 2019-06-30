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
        text=f'{symbol} Candlestick Chart',
        xref='paper',
        x=0
    ),
)

fig = go.Figure(data=data, layout=layout)
candlestick_filepath = os.path.join(os.path.dirname(__file__), "..", "chart", "candlestick.html")
plotly.offline.plot(fig, filename='candlestick.html')

print(f"GENERATED CHART: {candlestick_filepath}")
print("-------------------------")

plotly.tools.set_credentials_file(username='kms923', api_key='28X77R0cm1ATCaYZGbbY')

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

#removing % from string: https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python


##creating performance chart for all sectors

#Communication services (Comm_services) variables
a = list(one_day['Communication Services'])
a.remove('%')
one_day_converted_comm_svcs = float("".join(a))

b = list(one_month['Communication Services'])
b.remove('%')
one_month_converted_comm_svcs = float("".join(b))

c = list(three_month['Communication Services'])
c.remove('%')
three_month_converted_comm_svcs = float("".join(c))

d = list(YTD['Communication Services'])
d.remove('%')
YTD_converted_comm_svcs = float("".join(d))

#consumer discretionary (CD) variables
e = list(one_day['Consumer Discretionary'])
e.remove('%')
one_day_converted_CD = float("".join(e))

f = list(one_month['Consumer Discretionary'])
f.remove('%')
one_month_converted_CD = float("".join(f))

g = list(three_month['Consumer Discretionary'])
g.remove('%')
three_month_converted_CD = float("".join(g))

h = list(YTD['Consumer Discretionary'])
h.remove('%')
YTD_converted_CD = float("".join(h))

#consumer staples (cons_staples) variables
i = list(one_day['Consumer Staples'])
i.remove('%')
one_day_converted_cons_staples = float("".join(i))

j = list(one_month['Consumer Staples'])
j.remove('%')
one_month_converted_cons_staples = float("".join(j))

k = list(three_month['Consumer Staples'])
k.remove('%')
three_month_converted_cons_staples = float("".join(k))

l = list(YTD['Consumer Staples'])
l.remove('%')
YTD_converted_cons_staples = float("".join(l))

#Financials variables
m = list(one_day['Financials'])
m.remove('%')
one_day_converted_financials = float("".join(m))

n = list(one_month['Financials'])
n.remove('%')
one_month_converted_financials = float("".join(n))

o = list(three_month['Financials'])
o.remove('%')
three_month_converted_financials = float("".join(o))

p = list(YTD['Financials'])
p.remove('%')
YTD_converted_financials = float("".join(p))

#energy variables
q = list(one_day['Energy'])
q.remove('%')
one_day_converted_energy = float("".join(q))

r = list(one_month['Energy'])
r.remove('%')
one_month_converted_energy = float("".join(r))

s = list(three_month['Energy'])
s.remove('%')
three_month_converted_energy = float("".join(s))

t = list(YTD['Energy'])
t.remove('%')
YTD_converted_energy = float("".join(t))

#health care variables
u = list(one_day['Health Care'])
u.remove('%')
one_day_converted_health_care = float("".join(u))

v = list(one_month['Health Care'])
v.remove('%')
one_month_converted_health_care = float("".join(v))

w = list(three_month['Health Care'])
w.remove('%')
three_month_converted_health_care = float("".join(w))

x = list(YTD['Health Care'])
x.remove('%')
YTD_converted_health_care = float("".join(x))

#Industrials variables
y = list(one_day['Industrials'])
y.remove('%')
one_day_converted_industrials = float("".join(y))

z = list(one_month['Industrials'])
z.remove('%')
one_month_converted_industrials = float("".join(z))

aa = list(three_month['Industrials'])
aa.remove('%')
three_month_converted_industrials = float("".join(aa))

bb = list(YTD['Industrials'])
bb.remove('%')
YTD_converted_industrials = float("".join(bb))

#Information Technology (IT) variables
cc = list(one_day['Information Technology'])
cc.remove('%')
one_day_converted_IT = float("".join(cc))

dd = list(one_month['Information Technology'])
dd.remove('%')
one_month_converted_IT = float("".join(dd))

ee = list(three_month['Information Technology'])
ee.remove('%')
three_month_converted_IT = float("".join(ee))

ff = list(YTD['Information Technology'])
ff.remove('%')
YTD_converted_IT = float("".join(ff))

#Materials variables
gg = list(one_day['Materials'])
gg.remove('%')
one_day_converted_materials = float("".join(gg))

hh = list(one_month['Materials'])
hh.remove('%')
one_month_converted_materials = float("".join(hh))

ii = list(three_month['Materials'])
ii.remove('%')
three_month_converted_materials = float("".join(ii))

jj = list(YTD['Materials'])
jj.remove('%')
YTD_converted_materials = float("".join(jj))

#real estate (RE) variables
kk = list(one_day['Real Estate'])
kk.remove('%')
one_day_converted_real_estate = float("".join(kk))

ll = list(one_month['Real Estate'])
ll.remove('%')
one_month_converted_real_estate = float("".join(ll))

mm = list(three_month['Real Estate'])
mm.remove('%')
three_month_converted_real_estate = float("".join(mm))

nn = list(YTD['Real Estate'])
nn.remove('%')
YTD_converted_real_estate = float("".join(nn))

#utilities variables
oo = list(one_day['Utilities'])
oo.remove('%')
one_day_converted_utilities = float("".join(oo))

pp = list(one_month['Utilities'])
pp.remove('%')
one_month_converted_utilities = float("".join(pp))

qq = list(three_month['Utilities'])
qq.remove('%')
three_month_converted_utilities = float("".join(qq))

rr = list(YTD['Utilities'])
rr.remove('%')
YTD_converted_utilities = float("".join(rr))

trace1 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_comm_svcs, one_month_converted_comm_svcs, three_month_converted_comm_svcs, YTD_converted_comm_svcs],
    name='Communication Services',
    marker=dict(
        color='rgb(102, 178, 255)'
    )
)
trace2 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_CD, one_month_converted_CD, three_month_converted_CD, YTD_converted_CD],
    name='Consumer Discretionary',
    marker=dict(
        color='rgb(127, 0, 255)'
    )
)

trace3 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_cons_staples, one_month_converted_cons_staples, three_month_converted_cons_staples, YTD_converted_cons_staples],
    name='Consumer Staples',
    marker=dict(
        color='rgb(255, 153, 255)'
    )
)

trace4 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_financials, one_month_converted_financials, three_month_converted_financials, YTD_converted_financials],
    name='Financials',
    marker=dict(
        color='rgb(0, 255, 128)'
    )
)

trace5 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_energy, one_month_converted_energy, three_month_converted_energy, YTD_converted_energy],
    name='Energy',
    marker=dict(
        color='rgb(255, 0, 0)'
    )
)

trace6 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_health_care, one_month_converted_health_care, three_month_converted_health_care, YTD_converted_health_care],
    name='Health Care',
    marker=dict(
        color='rgb(241, 255, 28)'
    )
)

trace7 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_industrials, one_month_converted_industrials, three_month_converted_industrials, YTD_converted_industrials],
    name='Industrials',
    marker=dict(
        color='rgb(192, 192, 192)'
    )
)

trace8 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_IT, one_month_converted_IT, three_month_converted_IT, YTD_converted_IT],
    name='Information Technology',
    marker=dict(
        color='rgb(62, 17, 239)'
    )
)

trace9 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_materials, one_month_converted_materials, three_month_converted_materials, YTD_converted_materials],
    name='Materials',
    marker=dict(
        color='rgb(255, 153, 51)'
    )
)

trace10 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_real_estate, one_month_converted_real_estate, three_month_converted_real_estate, YTD_converted_real_estate],
    name='Real Estate',
    marker=dict(
        color='rgb(26, 118, 255)'
    )
)

trace11 = go.Bar(
    x=['1Day Perf. (%)', '1M Perf. (%)', '3M Perf. (%)', 'YTD Perf. (%)'],
    y=[one_day_converted_utilities, one_month_converted_utilities, three_month_converted_utilities, YTD_converted_utilities],
    name='Utilities',
    marker=dict(
        color='rgb(96, 96, 96)'
    )
)


data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8, trace9, trace10, trace11]
layout = go.Layout(
    title='Sector Performance Chart',
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

