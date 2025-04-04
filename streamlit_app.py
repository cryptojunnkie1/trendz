import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to fetch top 300 dividend stocks (placeholder)
def fetch_top_dividend_stocks():
    # Placeholder: Replace with actual data fetching logic
    tickers = ['AAPL', 'MSFT', 'KO', 'PG', 'JNJ']  # Example tickers
    data = {
        'Ticker': tickers,
        'Dividend Yield': [0.005, 0.008, 0.03, 0.025, 0.015],
        'Payout Ratio': [0.25, 0.30, 0.60, 0.50, 0.40],
        'EPS': [5.0, 6.0, 2.0, 3.0, 4.0],
        'PE Ratio': [28, 35, 20, 22, 24]
    }
    return pd.DataFrame(data)

# Function to calculate hypothetical returns
def calculate_returns(ticker, shares, investment):
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1y")
    
    current_price = hist['Close'][-1]
    price_one_year_ago = hist['Close'][0]
    
    annual_dividend = stock_data.info['dividendRate']
    total_dividends = shares * annual_dividend
    
    price_change = (current_price - price_one_year_ago) * shares
    total_return = total_dividends + price_change
    
    return total_dividends, price_change, total_return, current_price, price_one_year_ago

# Streamlit app layout
st.title("Dividend Stock Portfolio Builder")

# Fetch and display top dividend stocks
df_stocks = fetch_top_dividend_stocks()
st.subheader("Top Dividend Stocks")
st.dataframe(df_stocks)

# User input for selected stocks
selected_tickers = st.multiselect("Select stocks for analysis:", df_stocks['Ticker'].tolist())

# Input for investment amount
investment_amount = st.number_input("Enter your hypothetical investment amount ($):", min_value=0)

if selected_tickers and investment_amount > 0:
    results = []
    
    for ticker in selected_tickers:
        shares = investment_amount // df_stocks[df_stocks['Ticker'] == ticker]['Dividend Yield'].values[0]
        total_dividends, price_change, total_return, current_price, price_one_year_ago = calculate_returns(ticker, shares, investment_amount)
        
        results.append({
            "Ticker": ticker,
            "Total Dividends": total_dividends,
            "Price Change": price_change,
            "Total Return": total_return,
            "Current Price": current_price,
            "Price One Year Ago": price_one_year_ago
        })
    
    results_df = pd.DataFrame(results)
    st.subheader("Investment Analysis Results")
    st.dataframe(results_df)

    # Display hypothetical investment message
    for index, row in results_df.iterrows():
        st.write(f"If you had invested ${investment_amount} in {row['Ticker']}, you would have earned ${row['Total Dividends']:.2f} in dividends over the past year.")
        st.write(f"The stock price changed from ${row['Price One Year Ago']:.2f} to ${row['Current Price']:.2f}, resulting in a total return of ${row['Total Return']:.2f}.")

