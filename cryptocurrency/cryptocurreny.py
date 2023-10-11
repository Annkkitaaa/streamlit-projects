# Libraries used
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json

# Page layout
st.set_page_config(layout="wide")

# Title
image = Image.open(r"C:\Users\Ankita Singh\OneDrive\Desktop\streamlit projects\cryptocurrency\logo.jpg")  # Ensure that the image file is in the same directory as your script.
st.image(image, width=500)
st.title('Crypto Price App')
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrencies from **CoinMarketCap**!
""")

# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
* **Credit:** Web scraper adapted from the Medium article [Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf) written by [Bryan Feng](https://medium.com/@bryanf).
""")

# Sidebar + Main panel
col1 = st.sidebar
col2, col3 = st.columns((2, 1))

# Sidebar - Currency price unit
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

# Web scraping of CoinMarketCap data
@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

    coin_name, coin_symbol, market_cap, percent_change_1h, percent_change_24h, percent_change_7d, price, volume_24h = [], [], [], [], [], [], [], []

    for item in listings:
        coin_name.append(item['slug'])
        coin_symbol.append(item['symbol'])
        quote = item['quote'][currency_price_unit]
        price.append(quote['price'])
        percent_change_1h.append(quote['percent_change_1h'])
        percent_change_24h.append(quote['percent_change_24h'])
        percent_change_7d.append(quote['percent_change_7d'])
        market_cap.append(quote['market_cap'])
        volume_24h.append(quote['volume_24h'])

    data = {
        'coin_name': coin_name,
        'coin_symbol': coin_symbol,
        'price': price,
        'percent_change_1h': percent_change_1h,
        'percent_change_24h': percent_change_24h,
        'percent_change_7d': percent_change_7d,
        'market_cap': market_cap,
        'volume_24h': volume_24h
    }

    df = pd.DataFrame(data)
    return df

df = load_data()

# Sidebar - Cryptocurrency selections
sorted_coin = sorted(df['coin_symbol'].unique())
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[df['coin_symbol'].isin(selected_coin)]

# Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin.head(num_coin)

# Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame', ['7d', '24h', '1h'])
selected_percent_timeframe = f'percent_change_{percent_timeframe}'

# Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrencies')
col2.write(f'Data Dimension: {df_selected_coin.shape[0]} rows and {df_selected_coin.shape[1]} columns.')
col2.dataframe(df_coins)

# Download CSV data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# Preparing data for Bar plot of % Price change
col2.subheader('Table of % Price Change')
df_change = df_coins[['coin_symbol', selected_percent_timeframe]]
df_change.set_index('coin_symbol', inplace=True)
df_change['positive_percent_change'] = df_change[selected_percent_timeframe] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader('Bar plot of % Price Change')

if sort_values == 'Yes':
    df_change = df_change.sort_values(by=[selected_percent_timeframe], ascending=False)

col3.write(f'{percent_timeframe} period')
plt.figure(figsize=(8, 10))
df_change[selected_percent_timeframe].plot(kind='barh', color=df_change.positive_percent_change.map({True: 'g', False: 'r'}))
col3.pyplot(plt)
