import matplotlib.pyplot as plt
import streamlit as st

class PortfolioAnalysisTool:
    def __init__(self):
        self.portfolio = []

    def add_asset(self, name, asset_type, value, allocation_percentage):
        """Add an asset to the portfolio."""
        self.portfolio.append({
            "name": name,
            "type": asset_type,
            "value": value,
            "allocation_percentage": allocation_percentage
        })

    def view_portfolio(self):
        """Display the portfolio details."""
        total_value = sum(asset['value'] for asset in self.portfolio)
        st.write("## Portfolio Overview")
        st.write("### Asset Details:")
        for asset in self.portfolio:
            st.write(f"Name: {asset['name']}, Type: {asset['type']}, Value: ${asset['value']:.2f}, "
                     f"Allocation: {asset['allocation_percentage']}%")
        st.write(f"### Total Portfolio Value: ${total_value:.2f}")

    def plot_allocation_pie_chart(self):
        """Plot a pie chart of the portfolio's asset allocation."""
        if not self.portfolio:
            st.warning("No assets in portfolio to display a pie chart.")
            return
        labels = [asset['name'] for asset in self.portfolio]
        sizes = [asset['allocation_percentage'] for asset in self.portfolio]
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title('Portfolio Asset Allocation')
        st.pyplot(fig)

    def asset_allocation_analysis(self):
        """Analyze the portfolio's asset allocation."""
        allocation = {}
        for asset in self.portfolio:
            allocation[asset['type']] = allocation.get(asset['type'], 0) + asset['allocation_percentage']

        st.write("## Asset Allocation Analysis")
        for asset_type, percentage in allocation.items():
            st.write(f"{asset_type}: {percentage:.2f}%")

        if sum(allocation.values()) != 100:
            st.warning("Warning: Allocation percentages do not sum up to 100%.")

    def risk_assessment(self):
        """Provide a simple risk assessment based on asset types."""
        risk_levels = {"Stocks": "High", "Bonds": "Medium", "Cash": "Low", "Real Estate": "Medium"}

        st.write("## Risk Assessment")
        for asset in self.portfolio:
            risk = risk_levels.get(asset['type'], "Unknown")
            st.write(f"Asset: {asset['name']}, Type: {asset['type']}, Risk Level: {risk}")

# Streamlit Interface
def main():
    st.title("Portfolio Analysis Tool")

    # Session State to Persist Portfolio Data
    if "portfolio_tool" not in st.session_state:
        st.session_state["portfolio_tool"] = PortfolioAnalysisTool()
    portfolio_tool = st.session_state["portfolio_tool"]

    # Sidebar: Add Asset
    with st.sidebar:
        st.header("Add Asset")
        name = st.text_input("Asset Name")
        asset_type = st.selectbox("Asset Type", ["Stocks", "Bonds", "Cash", "Real Estate"])
        value = st.number_input("Value ($)", min_value=0.0, step=100.0)
        allocation_percentage = st.number_input("Allocation Percentage (%)", min_value=0.0, max_value=100.0, step=1.0)

        if st.button("Add Asset"):
            portfolio_tool.add_asset(name, asset_type, value, allocation_percentage)
            st.success(f"Added {name} to the portfolio!")

    # Main Content: View and Analyze Portfolio
    if portfolio_tool.portfolio:
        portfolio_tool.view_portfolio()
        portfolio_tool.plot_allocation_pie_chart()
        portfolio_tool.asset_allocation_analysis()
        portfolio_tool.risk_assessment()
    else:
        st.info("No assets in the portfolio. Use the sidebar to add assets.")

if __name__ == "__main__":
    main()
