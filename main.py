import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Helper functions for portfolio metrics
def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate (CAGR)."""
    return ((end_value / start_value) ** (1 / years) - 1) * 100

def calculate_sharpe_ratio(portfolio_returns, risk_free_rate, std_dev):
    """Calculate Sharpe Ratio."""
    return (np.mean(portfolio_returns) - risk_free_rate) / std_dev

def calculate_portfolio_volatility(weights, covariance_matrix):
    """Calculate portfolio volatility."""
    return np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))

# Main Portfolio Tool class
class PortfolioAnalysisTool:
    def __init__(self):
        self.portfolio = pd.DataFrame(columns=["Name", "Type", "Value", "Allocation (%)", "Return (%)", "Volatility (%)"])
        self.benchmark = None

    def add_asset(self, name, asset_type, value, allocation_percentage, expected_return, volatility):
        """Add an asset to the portfolio."""
        new_asset = pd.DataFrame({
            "Name": [name],
            "Type": [asset_type],
            "Value": [value],
            "Allocation (%)": [allocation_percentage],
            "Return (%)": [expected_return],
            "Volatility (%)": [volatility]
        })
        self.portfolio = pd.concat([self.portfolio, new_asset], ignore_index=True)

    def view_portfolio(self):
        """Display the portfolio."""
        st.write("## Portfolio Overview")
        st.dataframe(self.portfolio)
        total_value = self.portfolio["Value"].sum()
        st.write(f"### Total Portfolio Value: ${total_value:.2f}")

    def plot_allocation_pie_chart(self):
        """Plot asset allocation pie chart."""
        if self.portfolio.empty:
            st.warning("No assets in portfolio to display a pie chart.")
            return
        fig, ax = plt.subplots()
        ax.pie(
            self.portfolio["Allocation (%)"],
            labels=self.portfolio["Name"],
            autopct="%1.1f%%",
            startangle=140
        )
        ax.set_title("Portfolio Allocation")
        st.pyplot(fig)

    def calculate_portfolio_metrics(self):
        """Calculate and display key portfolio metrics."""
        if self.portfolio.empty:
            st.warning("No data available to calculate metrics.")
            return
        total_return = np.dot(self.portfolio["Allocation (%)"] / 100, self.portfolio["Return (%)"])
        total_volatility = calculate_portfolio_volatility(
            self.portfolio["Allocation (%)"].values / 100,
            np.diag(self.portfolio["Volatility (%)"].values)
        )
        st.write("## Portfolio Metrics")
        st.write(f"### Expected Annual Return: {total_return:.2f}%")
        st.write(f"### Portfolio Volatility: {total_volatility:.2f}%")

    def benchmark_comparison(self, benchmark_return):
        """Compare portfolio return with a benchmark."""
        if self.portfolio.empty:
            st.warning("No data available to compare with a benchmark.")
            return
        portfolio_return = np.dot(self.portfolio["Allocation (%)"] / 100, self.portfolio["Return (%)"])
        st.write("## Benchmark Comparison")
        st.write(f"### Portfolio Return: {portfolio_return:.2f}%")
        st.write(f"### Benchmark Return: {benchmark_return:.2f}%")
        if portfolio_return > benchmark_return:
            st.success("The portfolio is outperforming the benchmark.")
        else:
            st.error("The portfolio is underperforming compared to the benchmark.")

# Streamlit interface
def main():
    st.title("Advanced Portfolio Analysis Tool")

    # Initialize the tool
    if "portfolio_tool" not in st.session_state:
        st.session_state["portfolio_tool"] = PortfolioAnalysisTool()
    portfolio_tool = st.session_state["portfolio_tool"]

    # Sidebar for adding assets
    with st.sidebar:
        st.header("Add Asset")
        name = st.text_input("Asset Name")
        asset_type = st.selectbox("Asset Type", ["Stocks", "Bonds", "Cash", "Real Estate", "Other"])
        value = st.number_input("Value ($)", min_value=0.0, step=100.0)
        allocation = st.number_input("Allocation (%)", min_value=0.0, max_value=100.0, step=1.0)
        expected_return = st.number_input("Expected Return (%)", min_value=-100.0, max_value=100.0, step=0.1)
        volatility = st.number_input("Volatility (%)", min_value=0.0, max_value=100.0, step=0.1)

        if st.button("Add Asset"):
            portfolio_tool.add_asset(name, asset_type, value, allocation, expected_return, volatility)
            st.success(f"Added {name} to the portfolio.")

    # Main content
    portfolio_tool.view_portfolio()
    portfolio_tool.plot_allocation_pie_chart()
    portfolio_tool.calculate_portfolio_metrics()

    # Benchmark comparison
    benchmark_return = st.number_input("Benchmark Return (%)", min_value=-100.0, max_value=100.0, step=0.1)
    if st.button("Compare with Benchmark"):
        portfolio_tool.benchmark_comparison(benchmark_return)

if __name__ == "__main__":
    main()
