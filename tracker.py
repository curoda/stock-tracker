# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Cache the data fetching function to avoid redundant calls
@st.cache
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

# Main app
def main():
    st.title("Stock Performance Tracker")

    uploaded_file = st.file_uploader("Upload a spreadsheet with stock symbols, trade date, and score", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(df)

        # Define major stock indexes
        indexes = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC'
        }

        # Fetch stock data
        start_date = df['Date'].min()
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        
        stock_data = {}
        for index, row in df.iterrows():
            stock_data[row['Symbol']] = fetch_data(row['Symbol'], start_date, end_date)

        index_data = {}
        for name, ticker in indexes.items():
            index_data[name] = fetch_data(ticker, start_date, end_date)

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot stocks
        for symbol, data in stock_data.items():
            if st.checkbox(f"Show {symbol} with score {df[df['Symbol'] == symbol]['Score'].values[0]}?"):
                ax.plot(data.index, data, label=symbol)

        # Plot indexes
        for name, data in index_data.items():
            if st.checkbox(f"Show {name} index?"):
                ax.plot(data.index, data, label=name, linestyle='--')

        ax.set_title("Stock Performance Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()
