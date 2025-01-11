import streamlit as st
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt

# Helper function to fetch live prices
def fetch_price(asset_name, asset_type):
    """Fetch live price for a stock or cryptocurrency."""
    if asset_type == "Crypto":
        # Using CoinGecko API for crypto prices
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_name.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data.get(asset_name.lower(), {}).get("usd", None)
    elif asset_type == "Stock":
        # Replace 'YOUR_ALPHA_VANTAGE_API_KEY' with a valid key
        api_key = "YOUR_ALPHA_VANTAGE_API_KEY"
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={asset_name}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        return float(data["Global Quote"]["05. price"]) if "Global Quote" in data else None
    return None

# Portfolio Tool Class
class PortfolioTool:
    def __init__(self):
        self.transactions = pd.DataFrame(columns=["Asset", "Type", "Date", "Action", "Quantity", "Price"])
        self.portfolio = pd.DataFrame(columns=["Asset", "Type", "Average Price", "Current Price", "Quantity", "Value", "Unrealized P/L"])

    def add_transaction(self, asset_name, asset_type, date, action, quantity, price):
        """Add a buy/sell transaction for an asset."""
        new_transaction = pd.DataFrame({
            "Asset": [asset_name],
            "Type": [asset_type],
            "Date": [date],
            "Action": [action],
            "Quantity": [quantity if action == "Buy" else -quantity],
            "Price": [price]
        })
        self.transactions = pd.concat([self.transactions, new_transaction], ignore_index=True)
        self.update_portfolio()

    def update_portfolio(self):
        """Update portfolio data based on transactions."""
        if self.transactions.empty:
            return

        portfolio_summary = []
        for asset in self.transactions["Asset"].unique():
            asset_data = self.transactions[self.transactions["Asset"] == asset]
            asset_type = asset_data["Type"].iloc[0]
            total_quantity = asset_data["Quantity"].sum()

            if total_quantity > 0:
                # Calculate average price
                total_cost = (asset_data[asset_data["Quantity"] > 0]["Quantity"] * asset_data[asset_data["Quantity"] > 0]["Price"]).sum()
                average_price = total_cost / total_quantity

                # Fetch live price
                current_price = fetch_price(asset, asset_type)
                if current_price is None:
                    current_price = 0  # Fallback if API fails

                # Calculate unrealized P/L
                value = total_quantity * current_price
                unrealized_pl = value - (total_quantity * average_price)

                portfolio_summary.append({
                    "Asset": asset,
                    "Type": asset_type,
                    "Average Price": average_price,
                    "Current Price": current_price,
                    "Quantity": total_quantity,
                    "Value": value,
                    "Unrealized P/L": unrealized_pl
                })

        self.portfolio = pd.DataFrame(portfolio_summary)

    def display_portfolio(self):
        """Display portfolio summary."""
        st.write("## Portfolio Overview")
        if self.portfolio.empty:
            st.info("No assets in the portfolio. Add transactions to see your portfolio.")
        else:
            st.dataframe(self.portfolio)
            total_value = self.portfolio["Value"].sum()
            st.write(f"### Total Portfolio Value: ${total_value:.2f}")

            # Pie chart for allocation
            fig, ax = plt.subplots()
            ax.pie(self.portfolio["Value"], labels=self.portfolio["Asset"], autopct="%1.1f%%", startangle=140)
            ax.set_title("Portfolio Allocation")
            st.pyplot(fig)

# Streamlit Interface
def main():
    st.title("Stocks & Crypto Portfolio Tool")

    # Initialize the portfolio tool
    if "portfolio_tool" not in st.session_state:
        st.session_state["portfolio_tool"] = PortfolioTool()
    portfolio_tool = st.session_state["portfolio_tool"]

    # Sidebar: Add Transaction
    with st.sidebar:
        st.header("Add Transaction")
        asset_name = st.text_input("Asset Name (e.g., BTC, AAPL)")
        asset_type = st.selectbox("Asset Type", ["Crypto", "Stock"])
        date = st.date_input("Date")
        action = st.selectbox("Action", ["Buy", "Sell"])
        quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        price = st.number_input("Price ($)", min_value=0.0, step=0.01)

        if st.button("Add Transaction"):
            portfolio_tool.add_transaction(asset_name, asset_type, date, action, quantity, price)
            st.success(f"Transaction for {asset_name} added!")

    # Display portfolio
    portfolio_tool.display_portfolio()

    # Display transactions
    st.write("## Transaction History")
    if not portfolio_tool.transactions.empty:
        st.dataframe(portfolio_tool.transactions)

if __name__ == "__main__":
    main()
