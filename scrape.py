from bs4 import BeautifulSoup
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

product_url = input("Enter the product URL: ").strip()
target_price = float(input("Enter target price: "))


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def check_price():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.85 Safari/537.36"
        )
    }

    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    title_tag = soup.find(id="productTitle")
    if title_tag:
         title = title_tag.get_text(strip=True)
    else:
         print("Product title not found — possibly blocked or wrong page structure.")
         return

    price_str = soup.find("span",class_="a-price-whole").get_text(strip=True).replace(",", "")
    price = float(price_str.replace("₹", "").replace("$", "").replace(",", "").split(".")[0])

    print(f"Product: {title}")
    print(f"Current Price: {price}")

    if price <= target_price:
        send_email(title, price)

#Boilerplate
def send_email(title, price):
    subject = "Amazon Price Drop Alert!"
    body = (
        f"The price for '{title}' has dropped to ₹{price}!\n"
        f"Check it out here: {product_url}"
    )

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From']    = EMAIL_ADDRESS
    msg['To']      = RECEIVER_EMAIL
    msg.set_content(body)  # defaults to UTF-8

    # Send
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("Email sent!")

check_price()