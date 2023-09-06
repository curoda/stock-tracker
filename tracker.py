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

    uploaded_file = st.file_uploader("Upload a spreadsheet with stock symbols, purchase date, sell date, and score", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, parse_dates=['Purchase Date', 'Sell Date'])
        elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, parse_dates=['Purchase Date', 'Sell Date'])
        else:
            st.error("Unsupported file type. Please upload a .csv or .xlsx file.")
            return

        st.write(df)

        # Ensure there are no NaN values in the 'Purchase Date' column
        df = df.dropna(subset=['Purchase Date'])
        end_date = datetime.datetime.today().strftime('%Y-%m-%d')

        # Define major stock indexes
        indexes = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC'
        }

        # Group stocks by score
        grouped_stocks = df.groupby('Score')

        # Plot average percent change for stocks grouped by score alongside indexes
        fig, ax = plt.subplots(figsize=(10, 6))
        for score, group in grouped_stocks:
            if st.checkbox(f"Show performance for stocks with score {score}?"):
                avg_stock_data = pd.DataFrame()
                for index, row in group.iterrows():
                    stock_start_date = row['Purchase Date']
                    stock_end_date = row['Sell Date'] if not pd.isnull(row['Sell Date']) else end_date
                    data = fetch_data(row['Symbol'], stock_start_date, stock_end_date)
                    data = (data.pct_change() + 1).cumprod() - 1  # Convert to cumulative return
                    avg_stock_data[row['Symbol']] = data
                    ax.plot(data.index, data, label=row['Symbol'])  # Plot individual stock

                # Calculate average percent change for the group of stocks
                avg_stock_data['Average'] = avg_stock_data.mean(axis=1)

                # Calculate and display the difference between the group's average performance and each index
                differences = []
                for name, ticker in indexes.items():
                    index_data = fetch_data(ticker, avg_stock_data.index.min(), avg_stock_data.index.max())
                    index_data = (index_data.pct_change() + 1).cumprod() - 1  # Convert to cumulative return
                    difference = (avg_stock_data['Average'].iloc[-1] - index_data.iloc[-1]) * 100
                    differences.append(f"{difference:.2f}% more than the {name}")
                st.write(f"Score {score} stocks gained {' , '.join(differences)}.")

        ax.set_title("Stock Performance vs Indexes")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Return")
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()
