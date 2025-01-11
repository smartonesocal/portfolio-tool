import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

# API Helpers
def fetch_crypto_price(crypto_name):
    """Fetch live price for cryptocurrencies using CoinGecko API."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_name.lower()}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get(crypto_name.lower(), {}).get("usd", None)
    else:
        return None

def fetch_stock_price(stock_ticker):
    """Fetch live price for stocks using Alpha Vantage API."""
    api_key = "YOUR_ALPHA_VANTAGE_API_KEY"  # Replace with your Alpha Vantage API Key
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Global Quote" in data:
            return float(data["Global Quote"]["05. price"])
    return None

# Portfolio Class
class Portfolio:
    def __init__(self):
        self.transactions = pd.DataFrame(columns=["Asset", "Type", "Action", "Quantity", "Price", "Date"])
        self.portfolio = pd.DataFrame(columns=["Asset", "Type", "Average Price", "Current Price", "Quantity", "Value", "Unrealized P/L"])

    def add_transaction(self, asset, asset_type, action, quantity, price, date):
        """Add a buy/sell transaction."""
        new_transaction = pd.DataFrame({
            "Asset": [asset],
            "Type": [asset_type],
            "Action": [action],
            "Quantity": [quantity if action == "Buy" else -quantity],
            "Price": [price],
            "Date": [date]
        })
        self.transactions = pd.concat([self.transactions, new_transaction], ignore_index=True)
        self.update_portfolio()

    def update_portfolio(self):
        """Update portfolio based on transactions."""
        portfolio_data = []
        for asset in self.transactions["Asset"].unique():
            asset_transactions = self.transactions[self.transactions["Asset"] == asset]
            total_quantity = asset_transactions["Quantity"].sum()

            if total_quantity > 0:
                # Calculate average price
                total_cost = (asset_transactions[asset_transactions["Quantity"] > 0]["Quantity"] * asset_transactions["Price"]).sum()
                avg_price = total_cost / total_quantity

                # Fetch live price
                asset_type = asset_transactions["Type"].iloc[0]
                if asset_type == "Crypto":
                    current_price = fetch_crypto_price(asset)
                elif asset_type == "Stock":
                    current_price = fetch_stock_price(asset)
                else:
                    current_price = None

                if current_price is None:
                    current_price = 0

                # Calculate values
                current_value = total_quantity * current_price
                unrealized_pl = current_value - (total_quantity * avg_price)

                portfolio_data.append({
                    "Asset": asset,
                    "Type": asset_type,
                    "Average Price": avg_price,
                    "Current Price": current_price,
                    "Quantity": total_quantity,
                    "Value": current_value,
                    "Unrealized P/L": unrealized_pl
                })

        self.portfolio = pd.DataFrame(portfolio_data)

    def display_portfolio(self):
        """Display portfolio overview and allocation."""
        st.write("### Portfolio Overview")
        if self.portfolio.empty:
            st.info("No assets in the portfolio. Add transactions to see the portfolio.")
        else:
            st.dataframe(self.portfolio)
            total_value = self.portfolio["Value"].sum()
            st.write(f"**Total Portfolio Value:** ${total_value:,.2f}")

            # Allocation pie chart
            fig, ax = plt.subplots()
            ax.pie(self.portfolio["Value"], labels=self.portfolio["Asset"], autopct="%1.1f%%", startangle=140)
            ax.set_title("Portfolio Allocation")
            st.pyplot(fig)

    def display_transactions(self):
        """Display transaction history."""
        st.write("### Transaction History")
        if self.transactions.empty:
            st.info("No transactions recorded.")
        else:
            st.dataframe(self.transactions)

# Streamlit Interface
def main():
    st.title("Stocks & Crypto Portfolio Analysis Tool")
    st.sidebar.title("Add Transaction")

    # Initialize Portfolio
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = Portfolio()
    portfolio = st.session_state["portfolio"]

    # Sidebar Inputs
    asset = st.sidebar.text_input("Asset (e.g., BTC, AAPL)")
    asset_type = st.sidebar.selectbox("Type", ["Crypto", "Stock"])
    action = st.sidebar.selectbox("Action", ["Buy", "Sell"])
    quantity = st.sidebar.number_input("Quantity", min_value=0.0, step=0.1)
    price = st.sidebar.number_input("Price ($)", min_value=0.0, step=0.01)
    date = st.sidebar.date_input("Date")

    if st.sidebar.button("Add Transaction"):
        portfolio.add_transaction(asset, asset_type, action, quantity, price, date)
        st.sidebar.success(f"Transaction for {asset} added successfully!")

    # Main Section
    portfolio.display_portfolio()
    portfolio.display_transactions()

if __name__ == "__main__":
    main()

            
               
