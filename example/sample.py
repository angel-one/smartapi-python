# package import statement
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect
# import SmartApi.smartExceptions #(for smartExceptions)


apiKey = "<YOUR API KEY>"
clientId = "<YOUR CLIENT ID>"
pin = "<PIN>"
totp = "<TOTP>"
correlation_id = "<YOUR CORRELATION ID>"



#create object of call
obj=SmartConnect(api_key=apiKey)

#login api call

data = obj.generateSession(clientId,pin,totp)

authToken = data['data']['jwtToken']
authToken = f'Bearer {authToken}'

refreshToken= data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()

#fetch User Profile
userProfile= obj.getProfile(refreshToken)



def error_json(correlation_id, code, msg):
    errorJson = {
        "correlationID": correlation_id,
        "errorCode": code,
        "errorMessage": msg
    }
    return errorJson


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
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    print(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    print(error_json(correlation_id, code, msg))

    # print("Order placement failed: {}".format(e.message))
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
    rule_id=obj.gttCreateRule(gttCreateParams)
    print("The GTT rule id is: {}".format(rule_id))
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    print(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    print(error_json(correlation_id, code, msg))
    # print("GTT Rule creation failed: {}".format(e.message))
    
#gtt rule list
try:
    status=["FORALL"] #should be a list
    page=1
    count=10
    lists=obj.gttLists(status,page,count)
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    print(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    print(error_json(correlation_id, code, msg))
    # print("GTT Rule List failed: {}".format(e.message))

#Historic api
try:
    historicParam={
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2021-02-08 09:00", 
    "todate": "2021-02-08 09:16"
    }
    obj.getCandleData(historicParam)
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    print(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    print(error_json(correlation_id, code, msg))
    # print("Historic Api failed: {}".format(e.message))
    
# logout
try:
    logout=obj.terminateSession('Your Client Id')
    print("Logout Successfull")
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    print(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    print(error_json(correlation_id, code, msg))
    # print("Logout failed: {}".format(e.message))



# ## WebSocket
# from SmartApi import WebSocket

# FEED_TOKEN= "your feed token"
# CLIENT_CODE="your client Id"
# token="channel you want the information of" #"nse_cm|2885&nse_cm|1594&nse_cm|11536"
# task="task" #"mw"|"sfi"|"dp"
# ss = WebSocket(FEED_TOKEN, CLIENT_CODE)

# def on_tick(ws, tick):
#     print("Ticks: {}".format(tick))

# def on_connect(ws, response):
#     ws.websocket_connection() # Websocket connection  
#     ws.send_request(token,task) 
    
# def on_close(ws, code, reason):
#     ws.stop()

# # Assign the callbacks.
# ss.on_ticks = on_tick
# ss.on_connect = on_connect
# ss.on_close = on_close

# ss.connect()



from SmartApi.smartWebSocketV2 import SmartWebSocketV2



AUTH_TOKEN = authToken
API_KEY = 'uU2XbJU1'
CLIENT_CODE = 'A50193197'
FEED_TOKEN = feedToken

action = 1
mode = 1

token_list = [
               {
                    "exchangeType": 5,
                    "tokens": [
                         "244999",
                         "246083"
                    ]
               }]

# token_list = [{"exchangeType": 1, "tokens": ["26009"]}]

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

def on_data(wsapp, message):
    print("Ticks: {}".format(message))


def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    print(error)


def on_close(wsapp):
    print("Close")


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()


