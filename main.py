import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import openai  # For news summarization

# --- API Keys ---
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"  # Get from https://newsapi.org
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Get from https://openai.com

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

# Helper functions
def fetch_stock_news(symbol):
    """Fetch stock-related news using NewsAPI."""
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json()["articles"]
        return articles
    else:
        st.error(f"Failed to fetch news for {symbol}. Check API Key or symbol.")
        return []

def fetch_crypto_news(crypto_name):
    """Fetch crypto-related news using CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["coins"]
        return [
            {
                "title": coin["item"]["name"],
                "url": f"https://www.coingecko.com/en/coins/{coin['item']['id']}",
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            for coin in data
        ]
    else:
        st.error(f"Failed to fetch crypto news. Check API.")
        return []

def summarize_news(text):
    """Summarize news using OpenAI GPT."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following news article in a concise and actionable way:\n\n{text}",
            max_tokens=100,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        st.error(f"OpenAI summarization failed: {e}")
        return "Unable to summarize this news article."

def analyze_sentiment(text):
    """Perform sentiment analysis on the news article using OpenAI."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Analyze the sentiment of the following text as Positive, Negative, or Neutral:\n\n{text}",
            max_tokens=10,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        st.error(f"Sentiment analysis failed: {e}")
        return "Unknown"

# Streamlit App
def main():
    st.title("Stocks & Crypto News Aggregator")
    st.sidebar.title("Watchlist Manager")

    # --- Watchlist Management ---
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = []

    st.sidebar.header("Add to Watchlist")
    asset_name = st.sidebar.text_input("Asset Name (e.g., AAPL, BTC)")
    asset_type = st.sidebar.selectbox("Asset Type", ["Stock", "Crypto"])
    if st.sidebar.button("Add Asset"):
        st.session_state["watchlist"].append({"name": asset_name, "type": asset_type})
        st.sidebar.success(f"Added {asset_name} to the watchlist.")

    # Display current watchlist
    st.sidebar.subheader("Your Watchlist")
    if st.session_state["watchlist"]:
        for asset in st.session_state["watchlist"]:
            st.sidebar.write(f"- {asset['name']} ({asset['type']})")
    else:
        st.sidebar.info("Your watchlist is empty.")

    # --- News Aggregation ---
    st.header("Aggregated News Feed")
    if st.session_state["watchlist"]:
        for asset in st.session_state["watchlist"]:
            st.subheader(f"News for {asset['name']} ({asset['type']})")

            # Fetch news based on asset type
            if asset["type"] == "Stock":
                news_articles = fetch_stock_news(asset["name"])
            elif asset["type"] == "Crypto":
                news_articles = fetch_crypto_news(asset["name"])
            else:
                news_articles = []

            # Display news articles
            if news_articles:
                for article in news_articles:
                    st.markdown(f"**Title:** {article['title']}")
                    st.markdown(f"**URL:** [Read more]({article['url']})")
                    st.markdown(f"**Date:** {article['date']}")

                    # Summarize news
                    summary = summarize_news(article["title"])
                    st.write(f"**Summary:** {summary}")

                    # Sentiment Analysis
                    sentiment = analyze_sentiment(article["title"])
                    st.write(f"**Sentiment:** {sentiment}")
                    st.write("---")
            else:
                st.write(f"No news available for {asset['name']}.")

    else:
        st.info("Add assets to your watchlist to see news.")

if __name__ == "__main__":
    main()
