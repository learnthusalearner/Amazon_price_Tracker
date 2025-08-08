import os
import time
import threading
from datetime import datetime

import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Amazon Price Tracker", layout="centered")
st.title("🛒 Amazon Smart Price Tracker")
st.markdown("Keep an eye on your product and get notified when the price drops.")

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

CSV_FILE = "price_history.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.85 Safari/537.36"
    )
}

def log_price(timestamp, price):
    entry = pd.DataFrame([[timestamp, price]], columns=["Timestamp", "Price"])
    write_header = not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0
    entry.to_csv(CSV_FILE, mode='a', header=write_header, index=False)


def send_email(product_title, price, product_url):
    subject = "Amazon Price Drop Alert!"
    body = (
        f"The price for '{product_title}' has dropped to ₹{price}!\n"
        f"Check it out here: {product_url}"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER_EMAIL
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    st.success("📧 Email sent successfully!")


def check_price(product_url, target_price):
    """
    Scrape Amazon product page for the current price.
    Log the price and send email if below target.
    """
    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Get product title
        title_tag = soup.find(id="productTitle")
        if not title_tag:
            st.error("❌ Could not find product title. Please check the URL.")
            return None

        title = title_tag.get_text(strip=True)

        # Get product price
        price_tag = soup.find("span", class_="a-price-whole")
        if not price_tag:
            st.error("❌ Could not find product price.")
            return None

        price = float(price_tag.get_text(strip=True)
                      .replace("₹", "")
                      .replace(",", "")
                      .split(".")[0])

        # Save price to history
        log_price(datetime.now(), price)

        # Check for price drop
        if price <= target_price:
            send_email(title, price, product_url)

        return title, price

    except Exception as e:
        st.error(f"⚠️ Error while checking price: {e}")
        return None


def plot_price_history():
    """Read the CSV and plot the price changes over time."""
    if not os.path.exists(CSV_FILE):
        st.info("No price history available yet.")
        return

    try:
        df = pd.read_csv(CSV_FILE, parse_dates=["Timestamp"])
        if df.empty or "Timestamp" not in df.columns:
            st.warning("Price history file is missing required columns.")
            return

        df.sort_values("Timestamp", inplace=True)

        fig, ax = plt.subplots()
        ax.plot(df["Timestamp"], df["Price"], marker="o", color="green", linestyle="-")
        ax.set_title("Price Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price (₹)")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Couldn't plot history: {e}")


def start_background_check(product_url, target_price):
    """Run price check in a background thread every 12 hours."""
    def job():
        while True:
            check_price(product_url, target_price)
            time.sleep(43200)  # 12 hours

    threading.Thread(target=job, daemon=True).start()


st.markdown("### 📝 Enter Product Details")
product_url = st.text_input("🔗 Product URL")
target_price = st.number_input("🎯 Target Price (₹)", min_value=0.0, format="%.2f")

st.markdown("---")
st.markdown("### 🚀 Actions")
col1, _, col2 = st.columns(3)

with col1:
    if st.button("▶️ Start Tracking"):
        if product_url and target_price:
            st.success("✅ Tracking started. First check in progress...")
            start_background_check(product_url, target_price)
            result = check_price(product_url, target_price)
            if result:
                title, price = result
                st.markdown(f"**🛍 Product:** {title}")
                st.markdown(f"**💰 Current Price:** ₹{price}")
        else:
            st.warning("⚠️ Please provide both product URL and target price.")

with col2:
    if st.button("📂 Show Price Data"):
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.markdown("### 📄 Price History Data")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ No price history data yet.")

st.markdown("---")
st.markdown("### 📈 Visualize Price Trends")
if st.button("📊 Show Price Graph"):
    plot_price_history()

st.markdown("---")
st.markdown("### 📧 Manual Email Alert")
with st.expander("📨 Send Email Now"):
    if product_url:
        confirm = st.radio("Send alert email now?", ("No", "Yes"), horizontal=True)
        if confirm == "Yes" and st.button("✅ Confirm & Send Email"):
            result = check_price(product_url, target_price)
            if result:
                title, price = result
                send_email(title, price, product_url)
                st.success("✅ Email sent.")
    else:
        st.warning("⚠️ Please enter the product URL first.")

st.markdown("---")
st.markdown("### 🧹 Manage History")
if st.button("🗑 Reset Price History"):
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        st.success("🧼 Price history deleted.")
    else:
        st.info("📭 No history file to delete.")
