# SMARTAPI-PYTHON

SMARTAPI-PYTHON is a Python library for interacting with Angel's Trading platform  ,that is a set of REST-like HTTP APIs that expose many capabilities required to build stock market investment and trading platforms. It lets you execute orders in real time..


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install smartapi-python.

```bash
pip install -r requirements_dev.txt       # for downloading the other required packages
```

Download the following packages
```bash
pip install pyotp
pip install logzero
pip install websocket-client    
```
For Downloading pycryptodome package
```bash
pip uninstall pycrypto
pip install pycryptodome    
```

## Usage

```python
# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger

api_key = 'Your Api Key'
username = 'Your client code'
pwd = 'Your pin'
smartApi = SmartConnect(api_key)
try:
    token = "Your QR value"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
# Method 1: login api using password.
data = smartApi.generateSession(username, pwd, totp)

if data.get('status', False):
    logger.info(f"Your login data: {data}")
    
    # To get authToken/jwtToken.
    authToken = data['data']['jwtToken']
    # To get refreshToken.
    refreshToken = data['data']['refreshToken']
    # To get the feedtoken.
    feedToken = smartApi.getfeedToken()

else:
    # Error msg if can't able to login with password(pin).
    logger.error(data)

    # Method 2: To login or generate authToken/jwtToken using RefreshToken.
    refreshToken = "Your refresh token from last login"
    smartApi.generateToken(refreshToken)

# fetch User Profile
res = smartApi.getProfile()

if not res.get('status'):
    logger.error(f"Can't login check your credentials: {res}.")

else:    
    #place order
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
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")

    #gtt rule creation
    try:
        gttCreateParams={
                "tradingsymbol" : "SBIN-EQ",
                "symboltoken" : "3045",
                "exchange" : "NSE", 
                "producttype" : "MARGIN",
                "transactiontype" : "BUY",
                "price" : 100000,
                "qty" : 10,
                "disclosedqty": 10,
                "triggerprice" : 200000,
                "timeperiod" : 365
            }
        rule_id=smartApi.gttCreateRule(gttCreateParams)
        logger.info(f"The GTT rule id is: {rule_id}")
    except Exception as e:
        logger.exception(f"GTT Rule creation failed: {e}")
        
    #gtt rule list
    try:
        status=["FORALL"] #should be a list
        page=1
        count=10
        lists=smartApi.gttLists(status,page,count)
    except Exception as e:
        logger.exception(f"GTT Rule List failed: {e}")

    #Historic api
    try:
        historicParam={
        "exchange": "NSE",
        "symboltoken": "3045",
        "interval": "ONE_MINUTE",
        "fromdate": "2021-02-08 09:00", 
        "todate": "2021-02-08 09:16"
        }
        smartApi.getCandleData(historicParam)
    except Exception as e:
        logger.exception(f"Historic Api failed: {e}")
    #logout
    try:
        logout=smartApi.terminateSession()
        logger.info("Logout Successfull")
    except Exception as e:
        logger.exception(f"Logout failed: {e}")

    ```

    ## Getting started with SmartAPI Websocket's
    ####### Websocket V2 sample code #######

    from SmartApi.smartWebSocketV2 import SmartWebSocketV2
    from logzero import logger

    AUTH_TOKEN = "authToken"
    API_KEY = "api_key"
    CLIENT_CODE = "client code"
    FEED_TOKEN = "feedToken"
    correlation_id = "abc123"
    action = 1
    mode = 1

    token_list = [
        {
            "exchangeType": 1,
            "tokens": ["26009"]
        }
    ]
    token_list1 = [
        {
            "action": 0,
            "exchangeType": 1,
            "tokens": ["26009"]
        }
    ]

    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))
        # close_connection()

    def on_open(wsapp):
        logger.info("on open")
        sws.subscribe(correlation_id, mode, token_list)
        # sws.unsubscribe(correlation_id, mode, token_list1)


    def on_error(wsapp, error):
        logger.error(error)


    def on_close(wsapp):
        logger.info("Close")



    def close_connection():
        sws.close_connection()


    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close

    sws.connect()
    ####### Websocket V2 sample code ENDS Here #######

    ########################### SmartWebSocket OrderUpdate Sample Code Start Here ###########################
    from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate
    client = SmartWebSocketOrderUpdate(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
    client.connect()
    ########################### SmartWebSocket OrderUpdate Sample Code End Here ###########################
```
##Change-log
##1.4.5
- Upgraded TLS Version

##1.4.7
- Added Error log file

##1.4.8
- Intgrated EDIS, Brokerage Calculator, Option Greek, TopGainersLosers, PutRatio API