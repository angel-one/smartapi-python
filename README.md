![SmartAPI Logo](https://smartapi.angelbroking.com/static/media/Smartapi-Logo-1200x212-Transparent.ef58ca94.png)
---
### 📢 SmartAPI Announcement: Static IP Requirement

#### 📌 Overview

As per NSE guidelines for retail algorithmic trading, SmartAPI access now requires a registered Static IP. **🗓 Effective:** 01-Apr-2026  

📚 [More Information](https://smartapi.angelbroking.com/exchange-regulations)

# SmartAPI - Python

SmartAPI - Python is a library for interacting with Angel Broking's trading platform. It provides REST-like HTTP APIs for building stock market investment and trading applications, including real-time order execution.

---

## 🔧 Installation

Use [pip](https://pip.pypa.io/en/stable/) to install the latest release:

```bash
pip install smartapi-python
```

---

## 🛠️ Dependency Setup

If you want to work with the latest code:

### 1. Clone the repository

```bash
git clone https://github.com/angel-one/smartapi-python.git
cd smartapi-python
```

### 2. Install dependencies

```bash
pip install -r requirements_dev.txt
```

---

## ⚡ Quick One-Liner (Optional)

To install development dependencies directly without cloning the repo:

```bash
pip install -r https://raw.githubusercontent.com/angel-one/smartapi-python/main/requirements_dev.txt

```

---

For cryptographic support, install `pycryptodome` (make sure to uninstall `pycrypto` first if it's installed):

```bash
pip uninstall pycrypto
pip install pycryptodome
```

---

## Usage

### Generate SmartAPI Session

```python
import pyotp
from SmartApi import SmartConnect
from SmartApi.loggerConfig import get_logger 

logger = get_logger(__name__, "INFO")

client_info = {
    "api_key": "Your Api Key",
    "client_id": "Your client code",
    "password": "Your pin",
    "totp_secret": "Your QR value",
}

try:
    # Generate TOTP token from secret
    totp = pyotp.TOTP(client_info["totp_secret"]).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

smartApi = SmartConnect(api_key=client_info["api_key"])
response = smartApi.generateSession(client_info["client_id"], client_info["password"], totp)

if response.get('status'):
    logger.info("Login successful!")
else:
    logger.error("Login failed!")
    logger.error(response)
```

### Get Profile

```python
profile = smartApi.getProfile(refreshToken=smartApi.getrefreshToken)
logger.info(profile)
```

---

### Place an Order

```python
try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "19500",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
    }
    orderid = smartApi.placeOrder(orderparams)
    logger.info(f"Order placed successfully. Order ID: {orderid}")
except Exception as e:
    logger.exception(f"Order placement failed: {e}")
```

---

### GTT Rules

```python
# Create GTT Rule
try:
    gttCreateParams = {
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "exchange": "NSE", 
        "producttype": "MARGIN",
        "transactiontype": "BUY",
        "price": 100000,
        "qty": 10,
        "disclosedqty": 10,
        "triggerprice": 200000,
        "timeperiod": 365
    }
    rule_id = smartApi.gttCreateRule(gttCreateParams)
    logger.info(f"GTT rule created. Rule ID: {rule_id}")
except Exception as e:
    logger.exception(f"GTT Rule creation failed: {e}")

# Fetch GTT Rule List
try:
    status = ["FORALL"]
    page = 1
    count = 10
    gtt_list = smartApi.gttLists(status, page, count)
    logger.info(f"GTT Rules: {gtt_list}")
except Exception as e:
    logger.exception(f"GTT Rule List fetch failed: {e}")
```

---

### Historical Data

```python
try:
    historicParam = {
        "exchange": "NSE",
        "symboltoken": "3045",
        "interval": "ONE_MINUTE",
        "fromdate": "2025-08-08 09:15", 
        "todate": "2025-09-08 15:15"
    }
    candle_data = smartApi.getCandleData(historicParam)
    logger.info(candle_data)
except Exception as e:
    logger.exception(f"Historic API failed: {e}")
```

---

### Logout

```python
try:
    logout = smartApi.terminateSession(client_info["client_id"])
    logger.info("Logout Successful")
except Exception as e:
    logger.exception(f"Logout failed: {e}")
```

---

## Getting Started with SmartAPI WebSocket

### WebSocket V2 Sample

```python
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from SmartApi.loggerConfig import get_logger 

logger = get_logger(__name__, "INFO")

AUTH_TOKEN = smartApi.getaccessToken
API_KEY = client_info["api_key"]
CLIENT_CODE = client_info["client_id"]
FEED_TOKEN = smartApi.getfeedToken

correlation_id = "abc123"
action = 1
mode = 1

token_list = [
    {
        "exchangeType": 1,
        "tokens": ["99926009", "99926000"]
    }
]

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

def on_data(wsapp, message):
    logger.info(f"Ticks: {message}")

def on_open(wsapp):
    logger.info("WebSocket opened")
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    logger.error(error)

def on_close(wsapp):
    logger.info("WebSocket closed")

sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()
```

---

### SmartWebSocket OrderUpdate Sample

```python
from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate

client = SmartWebSocketOrderUpdate(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
client.connect()
```

---

## Examples Folder

Check the `examples/` folder for ready-to-run scripts:

* `example_login.ipynb` — Generate SmartAPI session with login and TOTP
* `example_order.ipynb` — Place buy/sell orders and manage GTT rules
* `example_historical_data.ipynb` — Fetch historic candle data
* `example_market_data.ipynb` — Fetch live market data
* `example_websocketV2.ipynb` — Connect and subscribe to SmartAPI WebSocket V2

---

## Notes

* You need a valid API key and TOTP secret from Angel Broking's developer console.
* Wrap all API calls in try/except blocks to handle errors gracefully.
* Replace placeholders like `"Your Api Key"` and `"Your client code"` with your actual credentials.

---

Happy Trading! 🚀
