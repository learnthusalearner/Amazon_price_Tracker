# 🛒 Amazon Price Tracker

This Python script tracks the price of a product on Amazon and sends you an email alert when the price drops below your specified target.

## 📌 Features

- Scrapes product title and current price from Amazon.
- Sends an email notification if the price drops below your desired target.
- Uses environment variables for secure email credentials.
- Command-line based, easy to use.

---

## 🛠 Requirements

- Python 3.7+
- `requests`
- `beautifulsoup4`
- `python-dotenv`

## IMPORTANT THING TO DO
.env file should contain

- EMAIL_ADDRESS=your_email@gmail.com
- EMAIL_PASSWORD=your_email_password_or_app_password
- RECEIVER_EMAIL=receiver_email@gmail.com

## NOTE => go to email genratator and craete a 16 digit password after enabling 2 step verification and then instead EMAIL_PASSWORD = 16 digit key generated

