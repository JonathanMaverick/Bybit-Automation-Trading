# Bybit Automation Trading

>⚠️ Disclaimer:
>This repository is for educational purposes only. The code provided is not financial advice and should not be used for real trading without thorough testing and a full understanding of the risks involved. Always do your own research and consult a licensed financial advisor before making investment decisions.

## Overview
This repository contains a Python script for automating trading on the Bybit exchange using the Bybit API. The script is designed to place buy and sell orders based on specific conditions and manage open positions.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/JonathanMaverick/Bybit-Automation-Trading.git
cd Bybit-Automation-Trading
```
2. Install the dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the root directory and add your Bybit API key, secret, and other configurations
```env
API_KEY = ""
API_SECRET = ""
ACCOUNT_TYPE = ""
DISCORD_WEBHOOK = ""
```
4. Run the script:
```bash
python main.py
```


## Features

- Connect to Bybit API using WebSocket and REST API
- Fetch market data and account information
- Place buy and sell orders based on market conditions
- Manage open positions and close them based on specific conditions
- Using Discord Webhook to send notifications about trades and errors
<br/><img src="image/Discord_Image.png" alt="Discord Notification Example" width="600"/>
- Generate CSV file with trade history
<br/><img src="image/CSV_Image.png" alt="CSV Output Example" width="600"/>
- Generate Chart using Matplotlib and save it as an image
<br/><img src="image/Chart_Image.png" alt="Chart Example" width="600"/>
