from SmartApi.smartConnect import SmartConnect
import pyotp

api_key = 'api-key'
username = 'client-code'
pwd = 'pin'
smartApi = SmartConnect(api_key)
token = "QR-value code"
totp=pyotp.TOTP(token).now()
correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)
# print(data)
authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
feedToken = smartApi.getfeedToken()
# print("Feed-Token :", feedToken)
res = smartApi.getProfile(refreshToken)
# print("Res:", res)
smartApi.generateToken(refreshToken)
res=res['data']['exchanges']

try:
    orderparams = { "variety": "NORMAL",
                    "tradingsymbol": "RELIANCE-EQ",
                    "symboltoken": "122334875538",
                    "transactiontype": "BUY",
                    "exchange": "NSE",
                    "ordertype": "LIMIT",
                    "producttype": "DELIVERY",
                    "duration": "DAY",
                    "price": "2430",
                    "squareoff": "0",
                    "stoploss": "0",
                    "quantity": "8"
                    }
    orderId=smartApi.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
    if isinstance(e, TypeError):
        print("Order placement failed: Invalid request parameters.")
    else:
        print("Order placement failed: {}".format(str(e)))