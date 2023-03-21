########################################################## smartWebSocketV2.py constants ##########################################################


ROOT_URI = "ws://smartapisocket.angelone.in/smart-stream"
HEART_BEAT_MESSAGE = "ping"
HEAR_BEAT_INTERVAL = 30
LITTLE_ENDIAN_BYTE_ORDER = "<"
RESUBSCRIBE_FLAG = False
# HB_THREAD_FLAG = True
MAX_RETRY_ATTEMPT = 1

# Available Actions
SUBSCRIBE_ACTION = 1
UNSUBSCRIBE_ACTION = 0

# Possible Subscription Mode
LTP_MODE = 1
QUOTE = 2
SNAP_QUOTE = 3

# Exchange Type
NSE_CM = 1
NSE_FO = 2
BSE_CM = 3
BSE_FO = 4
MCX_FO = 5
NCX_FO = 7
CDE_FO = 13

# Subscription Mode Map
SUBSCRIPTION_MODE_MAP = {
    1: "LTP",
    2: "QUOTE",
    3: "SNAP_QUOTE"
}


########################################################## smartConnect.py constants ##########################################################
_rootUrl="https://apiconnect.angelbroking.com" #prod endpoint
_login_url="https://apiconnect.angelbroking.com" #prod endpoint

_default_timeout = 7  # In seconds

_routes = {
    "api.login":"/rest/auth/angelbroking/user/v1/loginByPassword",
    "api.logout":"/rest/secure/angelbroking/user/v1/logout",
    "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
    "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
    "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

    "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
    "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
    "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
    "api.order.book":"/rest/secure/angelbroking/order/v1/getOrderBook",
    
    "api.ltp.data": "/rest/secure/angelbroking/order/v1/getLtpData",
    "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
    "api.rms.limit": "/rest/secure/angelbroking/user/v1/getRMS",
    "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
    "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
    "api.convert.position": "/rest/secure/angelbroking/order/v1/convertPosition",

    "api.gtt.create":"/gtt-service/rest/secure/angelbroking/gtt/v1/createRule",
    "api.gtt.modify":"/gtt-service/rest/secure/angelbroking/gtt/v1/modifyRule",
    "api.gtt.cancel":"/gtt-service/rest/secure/angelbroking/gtt/v1/cancelRule",
    "api.gtt.details":"/rest/secure/angelbroking/gtt/v1/ruleDetails",
    "api.gtt.list":"/rest/secure/angelbroking/gtt/v1/ruleList",

    "api.candle.data":"/rest/secure/angelbroking/historical/v1/getCandleData"
}
