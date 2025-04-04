import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

# Title of the app
st.title("Stock Historical Analysis")

# Sidebar for user input
st.sidebar.header("User Input")

# Input for stock symbols
symbols = st.sidebar.text_input("Enter Stock Symbols (comma separated)", "^DJI")

# Input for date range
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2000-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Input for moving average period
ma_period = st.sidebar.slider("Moving Average Period (Days)", min_value=1, max_value=200, value=100)

# Fetching data using yfinance
@st.cache_data
def load_data(symbols, start, end):
    symbol_list = [symbol.strip() for symbol in symbols.split(",")]
    data = {symbol: yf.download(symbol, start=start, end=end) for symbol in symbol_list}
    return data

data = load_data(symbols, start_date, end_date)

# Define trading days for different periods
trading_days = {
    1: 252,
    2: 504,
    4: 1008,
    10: 2520
}

# Display the data for each symbol
for symbol, df in data.items():
    st.subheader(f"Historical Data for {symbol}")

    # Check if DataFrame is empty
    if df.empty:
        st.error(f"No data retrieved for {symbol}. Please check the symbol and date range.")
        continue  # Skip the rest of the loop for this symbol

    st.write(df)  # Display the historical data

    # Calculate the moving average for the specified period
    df['MA'] = df['Close'].rolling(window=ma_period, min_periods=1).mean()

    # Calculate moving averages for 2, 4, and 10 years
    for years, days in trading_days.items():
        df[f'MA_{years}Y'] = df['Close'].rolling(window=days, min_periods=1).mean()  # Ensure min periods for rolling

    # Plotting the data with moving averages
    st.subheader(f"Closing Prices with Moving Averages for {symbol}")
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.plot(df.index, df['MA'], label=f'{ma_period}-Day MA', color='orange', linewidth=2)

    for years in trading_days.keys():
        plt.plot(df.index, df[f'MA_{years}Y'], label=f'{years}-Year MA', linestyle='--')

    plt.title(f'{symbol} Closing Prices with Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()

    # Use mplcursors to add hover functionality
    cursor = mplcursors.cursor(hover=True)

    # Customizing the tooltip to show OHLCV values
    @cursor.connect("add")
    def on_add(sel):
        index = sel.index
        if index < len(df):
            date = df.index[index]
            open_price = df['Open'].iloc[index]
            high_price = df['High'].iloc[index]
            low_price = df['Low'].iloc[index]
            close_price = df['Close'].iloc[index]
            volume = df['Volume'].iloc[index]

            sel.annotation.set_text(
                f'Date: {date.date()}\n'
                f'Open: ${open_price:.2f}\n'
                f'High: ${high_price:.2f}\n'
                f'Low: ${low_price:.2f}\n'
                f'Close: ${close_price:.2f}\n'
                f'Volume: {volume:,}'
            )

    st.pyplot(plt)

    # Calculate daily returns
    daily_returns = df['Close'].pct_change()

    # Calculate performance metrics
    annual_returns = {}
    annual_volatility = {}
    total_returns = {}

    for years in trading_days.keys():
        recent_returns = daily_returns[-trading_days[years]:]
        annual_return = recent_returns.mean() * 252
        volatility = recent_returns.std() * (252 ** 0.5)

        # Get the price at the start and end of the period
        start_price = df['Close'].iloc[-trading_days[years]]
        end_price = df['Close'].iloc[-1]
        price_change = end_price - start_price

        # Total return percentage
        total_return_percentage = ((end_price - start_price) / start_price) * 100
        total_returns[years] = total_return_percentage.item()  # Ensure it's a scalar

        annual_returns[years] = (annual_return, start_price, end_price, price_change)
        annual_volatility[years] = volatility

    # Define a consistent investment amount
    investment_amount = 1000.0  # $1000 as the standard principal investment

    # Display performance metrics
    st.subheader("Performance Metrics")
    for years in trading_days.keys():
        # Calculate the dates relevant for the period
        start_date_period = df.index[-trading_days[years]]
        end_date_period = df.index[-1] if years != 10 else pd.to_datetime("2010-12-31")

        avg_return, start_price, end_price, price_change = annual_returns[years]
        
        # Ensure these are scalars
        avg_return = float(avg_return)
        start_price = float(start_price)
        end_price = float(end_price)
        price_change = float(price_change)
        
        volatility = float(annual_volatility[years])  # Ensure volatility is also a scalar
        total_return = total_returns[years]  # Get the total return percentage
        
        # Calculate how much $1000 could have become
        if start_price > 0:  # Check if start_price is valid
            shares_bought = investment_amount / start_price
            potential_value = shares_bought * end_price
        else:
            potential_value = 0  # If start_price is zero or invalid

        # Check if the period is still ongoing
        if end_date_period > pd.to_datetime("today"):
            period_status = "The investment period is still ongoing."
        else:
            period_status = "The investment period has concluded."

        # Update the output to include better formatting
        st.write(f"**{years}-Year Analysis:**")
        st.markdown(f"""
        - **Average Annual Return:** {avg_return:.2%}
        - **Starting Price:** ${start_price:.2f}
        - **Ending Price:** ${end_price:.2f}
        - **Price Change:** ${price_change:.2f}
        - **Total Return:** {total_return:.2f}%
        - **Annualized Volatility:** {volatility:.2%}
        - **Investment Amount:** ${investment_amount:,.2f}
        - **Potential value if invested:** ${potential_value:,.2f}
        - **Status:** {period_status}
        - **Period:** {start_date_period.date()} to {end_date_period.date()}
        """)

        # Add a solid line to separate periods
        st.markdown("---")  # Method 1
