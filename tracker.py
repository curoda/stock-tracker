# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Cache the data fetching function to avoid redundant calls
@st.cache_data
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

# Main app
def main():
    st.title("Stock Performance Tracker")

    uploaded_file = st.file_uploader("Upload a spreadsheet with stock symbols, trade date, and score", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, parse_dates=['Date'])
        elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, parse_dates=['Date'])
        else:
            st.error("Unsupported file type. Please upload a .csv or .xlsx file.")
            return

        st.write(df)

        # Ensure there are no NaN values in the 'Date' column
        df = df.dropna(subset=['Date'])
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        start_date = df['Date'].min()  # Define the start_date for fetching index data

        # Define major stock indexes
        indexes = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC'
        }

        # Fetch stock data and calculate percent change
        stock_data = {}
        for index, row in df.iterrows():
            stock_start_date = row['Date']
            data = fetch_data(row['Symbol'], stock_start_date, end_date)
            data = (data.pct_change() + 1).cumprod() - 1  # Convert to cumulative return
            stock_data[row['Symbol']] = data

        # Fetch index data and calculate percent change
        index_data = {}
        for name, ticker in indexes.items():
            data = fetch_data(ticker, start_date, end_date)
            data = (data.pct_change() + 1).cumprod() - 1  # Convert to cumulative return
            index_data[name] = data

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Group stocks by score and plot
        grouped_stocks = df.groupby('Score')
        for score, group in grouped_stocks:
            if st.checkbox(f"Show stocks with score {score}?"):
                for index, row in group.iterrows():
                    ax.plot(stock_data[row['Symbol']].index, stock_data[row['Symbol']], label=row['Symbol'])

        # Plot indexes
        for name, data in index_data.items():
            if st.checkbox(f"Show {name} index?"):
                ax.plot(data.index, data, label=name, linestyle='--')

        ax.set_title("Stock Performance Over Time (Cumulative Percent Change)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Return")
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()
