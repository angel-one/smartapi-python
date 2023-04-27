# package import statement
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect
from logzero import logger
# import SmartApi.smartExceptions #(for smartExceptions)

apiKey = "<YOUR API KEY>"
clientId = "<YOUR CLIENT ID>"
pin = "<PIN>"
totp = "<TOTP>"
correlation_id = "<correlation_id>"



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
        f"correlationID": correlation_id,
        f"errorCode": code,
        f"errorMessage": msg
    }
    return errorJson


# place order
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
	logger.info("The order id is: {}".format(orderId))
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    logger.error(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    logger.error(error_json(correlation_id, code, msg))

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
	logger.info("The GTT rule id is: {}".format(rule_id))
except TypeError:
	code = "E1001"
	msg = "Invalid Request Payload."
	logger.error(error_json(correlation_id, code, msg))
except Exception:
	code = "E1002"
	msg = "Invalid Request. Subscription Limit Exceeded."
	logger.error(error_json(correlation_id, code, msg))
    
#gtt rule list
try:
    status=["FORALL"] #should be a list
    page=1
    count=10
    lists=obj.gttLists(status,page,count)
    logger.info("The GTT List : {}".format(lists))
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    logger.error(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    logger.error(error_json(correlation_id, code, msg))

#Historic api
try:
    historicParam={
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2021-02-08 09:00", 
    "todate": "2021-02-08 09:16"
    }
    hist_param = obj.getCandleData(historicParam)
    logger.info("The Historic Params : {}".format(hist_param))
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    logger.error(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    logger.error(error_json(correlation_id, code, msg))
    
# logout
try:
    logout=obj.terminateSession('Your Client Id')
    logger.info("Logout Successfull")
except TypeError:
    code = "E1001"
    msg = "Invalid Request Payload."
    logger.error(error_json(correlation_id, code, msg))
except Exception:
    code = "E1002"
    msg = "Invalid Request. Subscription Limit Exceeded."
    logger.error(error_json(correlation_id, code, msg))



from SmartApi.smartWebSocketV2 import SmartWebSocketV2
'''
websocket
'''
AUTH_TOKEN = authToken
API_KEY = "<YOUR API KEY>"
CLIENT_CODE = "<YOUR CLIENT ID>"
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
    logger.info("Ticks: {}".format(message))


def on_open(wsapp):
    logger.info("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    logger.error(error)


def on_close(wsapp):
    logger.info("Close")


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()


