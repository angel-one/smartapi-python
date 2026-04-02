import json
import re
import socket
import ssl
import uuid

import requests
from urllib.parse import urljoin
from requests import get

from SmartApi.version import __version__, __title__
from SmartApi.loggerConfig import get_logger
import SmartApi.smartExceptions as ex

logger = get_logger(__name__, level="WARNING")


# ROOTURL = "https://openapisuat.angelbroking.com"
# LOGINURL ="https://smartapi.angelbroking.com/login"

ROOTURL = "https://apiconnect.angelone.in" #prod endpoint
LOGINURL = "https://smartapi.angelone.in/publisher-login" #prod endpoint

DEFAULT_TIMEOUT = 10  # (seconds)

# API endpoints used for authentication and user session management
ROUTES = {
    # Authentication endpoints
    "api.login": "/rest/auth/angelbroking/user/v1/loginByPassword",
    "api.logout": "/rest/secure/angelbroking/user/v1/logout",
    "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
    "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
    "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

    # Order related endpoints
    "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
    "api.order.placefullresponse": "/rest/secure/angelbroking/order/v1/placeOrder",
    "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
    "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
    "api.order.book": "/rest/secure/angelbroking/order/v1/getOrderBook",

    # Market data and trades
    "api.ltp.data": "/rest/secure/angelbroking/order/v1/getLtpData",
    "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
    "api.rms.limit": "/rest/secure/angelbroking/user/v1/getRMS",
    "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
    "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
    "api.convert.position": "/rest/secure/angelbroking/order/v1/convertPosition",

    # GTT (Good Till Triggered) endpoints
    "api.gtt.create": "/gtt-service/rest/secure/angelbroking/gtt/v1/createRule",
    "api.gtt.modify": "/gtt-service/rest/secure/angelbroking/gtt/v1/modifyRule",
    "api.gtt.cancel": "/gtt-service/rest/secure/angelbroking/gtt/v1/cancelRule",
    "api.gtt.details": "/rest/secure/angelbroking/gtt/v1/ruleDetails",
    "api.gtt.list": "/rest/secure/angelbroking/gtt/v1/ruleList",

    # Historical and market data
    "api.candle.data": "/rest/secure/angelbroking/historical/v1/getCandleData",
    "api.oi.data": "/rest/secure/angelbroking/historical/v1/getOIData",
    "api.market.data": "/rest/secure/angelbroking/market/v1/quote",
    "api.search.scrip": "/rest/secure/angelbroking/order/v1/searchScrip",
    "api.allholding": "/rest/secure/angelbroking/portfolio/v1/getAllHolding",

    # Detailed order info and margin
    "api.individual.order.details": "/rest/secure/angelbroking/order/v1/details/",
    "api.margin.api": "rest/secure/angelbroking/margin/v1/batch",
    "api.estimateCharges": "rest/secure/angelbroking/brokerage/v1/estimateCharges",

    # EDIS (Electronic DIS) related endpoints
    "api.verifyDis": "rest/secure/angelbroking/edis/v1/verifyDis",
    "api.generateTPIN": "rest/secure/angelbroking/edis/v1/generateTPIN",
    "api.getTranStatus": "rest/secure/angelbroking/edis/v1/getTranStatus",

    # Market analytics endpoints
    "api.optionGreek": "rest/secure/angelbroking/marketData/v1/optionGreek",
    "api.gainersLosers": "rest/secure/angelbroking/marketData/v1/gainersLosers",
    "api.putCallRatio": "rest/secure/angelbroking/marketData/v1/putCallRatio",
    "api.oIBuildup": "rest/secure/angelbroking/marketData/v1/OIBuildup",
    "api.nseIntraday": "rest/secure/angelbroking/marketData/v1/nseIntraday",
    "api.bseIntraday": "rest/secure/angelbroking/marketData/v1/bseIntraday",
}


class SmartConnect(object):
    """
    Main client class for interacting with the Angel One Smart API.
    
    This class handles session management, authentication, and configuration 
    required to interact with Angel One REST and WebSocket APIs. It supports 
    token-based authentication, proxy configuration, SSL handling, and 
    user metadata for secure access.
    
    """
    
    accept: str = "application/json"
    userType: str = "USER"
    sourceID: str = "WEB"

    def __init__(
        self,
        api_key: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        feed_token: str | None = None,
        userId: str | None = None,
        root: str | None = None,
        debug: bool = False,
        timeout: int | None = None,
        proxies: dict | None = None,
        pool: dict | None = None,
        disable_ssl: bool = False,
        accept: str | None = None,
        userType: str | None = None,
        sourceID: str | None = None,
        Authorization: str | None = None,
        clientPublicIP: str | None = None,
        clientMacAddress: str | None = None,
        clientLocalIP: str | None = None,
        privateKey: str | None = None,
    ):
    
        """
        Initialize the SmartConnect instance.

        This constructor sets up the Smart API client with all the necessary 
        authentication tokens, user information, and configuration needed to 
        interact with Angel One's REST and WebSocket APIs. It allows you to 
        manage sessions, make authenticated requests, subscribe to live market 
        data, and customize connection behavior through proxies, SSL options, 
        and user metadata.


        Parameters
        ----------
        api_key : str
            The Smart API key associated with the developer account.
        access_token : str, optional
            Access token received upon successful login.
        refresh_token : str, optional
            Refresh token used to renew the session without re-authentication.
        feed_token : str, optional
            Token used for subscribing to real-time market data feeds.
        userId : str, optional
            Unique identifier of the user (usually Angel One client ID).
        root : str, optional
            Base URL for the Smart API (defaults to the production endpoint).
        debug : bool, optional
            Enable verbose debug logging (default is False).
        timeout : int, optional
            Timeout value (in seconds) for HTTP requests (default is 7 seconds).
        proxies : dict, optional
            Dictionary of HTTP/HTTPS proxy settings (if needed for requests).
        pool : dict, optional
            Connection pool configuration (currently unused/reserved).
        disable_ssl : bool, optional
            Disable SSL verification (default is False). Useful for debugging.
        accept : str, optional
            Overrides the default `accept` header ("application/json").
        userType : str, optional
            Overrides the default user type ("USER").
        sourceID : str, optional
            Overrides the default source identifier ("WEB").
        Authorization : str, optional
            Bearer or JWT token to authorize API requests directly.
        clientPublicIP : str, optional
            Public IP address of the client (used for audit/tracking).
        clientMacAddress : str, optional
            MAC address of the client device (optional metadata).
        clientLocalIP : str, optional
            Local IP address of the client machine.
        privateKey : str, optional
            RSA private key string used for payload encryption (optional).

        Returns
        -------
        None
            This constructor does not return a value.

        """

        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or ROOTURL
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.Authorization = Authorization

        # Initialize client info 
        _clientPublicIP, _clientLocalIP, _clientMacAddress = self._get_client_info()

        self.clientPublicIP = clientPublicIP or _clientPublicIP
        self.clientLocalIP = clientLocalIP or _clientLocalIP
        self.clientMacAddress = clientMacAddress or _clientMacAddress
        
        self.privateKey = privateKey or api_key
        self.accept = accept or self.accept
        self.userType = userType or self.userType
        self.sourceID = sourceID or self.sourceID

        # Create SSL context and configure TLS versions
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.options |= ssl.OP_NO_TLSv1  # Disable TLS 1.0
        self.ssl_context.options |= ssl.OP_NO_TLSv1_1  # Disable TLS 1.1
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        # Initialize requests session with optional connection pooling
        if not disable_ssl:
            self.reqsession = requests.Session()
            if pool is not None:
                reqadapter = requests.adapters.HTTPAdapter(**pool)
                self.reqsession.mount("https://", reqadapter)
            else:
                reqadapter = requests.adapters.HTTPAdapter()
                self.reqsession.mount("https://", reqadapter)
            logger.info("Using connection pool for HTTPS requests.")
        else:
            # SSL disabled — fallback to requests without session
            self.reqsession = requests


    @staticmethod
    def _get_client_info() -> tuple[str, str, str]:
        """
        Retrieve client public IP, local IP, and MAC address.

        Returns:
            Tuple containing (public_ip, local_ip, mac_address).
        """
        try:
            public_ip: str = get("https://api.ipify.org").text.strip()
            hostname: str = socket.gethostname()
            local_ip: str = socket.gethostbyname(hostname)
        except Exception as e:
            logger.error(
                f"Exception while retrieving IP Address, using localhost IP: {e}"
            )
            public_ip = "106.193.147.98"  # fallback public IP
            local_ip = "127.0.0.1"  # fallback local IP

        mac_address: str = ":".join(re.findall("..", f"{uuid.getnode():012x}"))

        return public_ip, local_ip, mac_address

    @property
    def getUserId(self) -> str:
        """
        Get the current user ID.
        """
        return self.userId
    
    @property
    def getfeedToken(self) -> str:
        """
        Get the current feed token.
        """
        return self.feed_token

    @property
    def getaccessToken(self) -> str:
        """
        Get the access token.
        """
        return self.access_token
    
    @property
    def getrefreshToken(self) -> str:
        """
        Get the refresh token.
        """
        return self.refresh_token
    
    @property
    def login_url(self) -> str:
        """
        Generate SmartAPI login URL.
        """
        return "%s?api_key=%s" % (LOGINURL, self.api_key)
    
    
    def requestHeaders(self) -> dict:
        """
        Return HTTP headers for API requests.
        """
        return {
            "Content-type": self.accept,
            "X-ClientLocalIP": self.clientLocalIP,
            "X-ClientPublicIP": self.clientPublicIP,
            "X-MACAddress": self.clientMacAddress,
            "Accept": self.accept,
            "X-PrivateKey": self.privateKey,
            "X-UserType": self.userType,
            "X-SourceID": self.sourceID
        }

    def setSessionExpiryHook(self, method) -> None:
        """
        Set callback for session expiry event.
        """
        if not callable(method):
            raise TypeError("Invalid input type. Only functions are accepted.")
        self.session_expiry_hook = method

    def setUserId(self, id: str) -> None:
        """
        Set the user ID value.
        """
        self.userId = id

    def setAccessToken(self, access_token: str) -> None:
        """
        Set the access token string.
        """
        self.access_token = access_token

    def setRefreshToken(self, refresh_token: str) -> None:
        """
        Set the refresh token string.
        """
        self.refresh_token = refresh_token

    def setFeedToken(self, feedToken: str) -> None:
        """
        Set the market feed token.
        """
        self.feed_token = feedToken


    def _request(
        self, 
        route: str, 
        method: str, 
        parameters: dict = None
    ) -> dict | bytes:
        """
        Make a low-level HTTP API request.
        """
        params = parameters.copy() if parameters else {}

        uri = ROUTES[route].format(**params)
        url = urljoin(self.root, uri)

        headers = self.requestHeaders()

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        if self.debug:
            logger.debug(f"Request: {method} {url} {params} {headers}")

        try:
            r = requests.request(
                method,
                url,
                data=json.dumps(params) if method in ["POST", "PUT"] else None,
                params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                headers=headers,
                verify=not self.disable_ssl,
                allow_redirects=True,
                timeout=self.timeout,
                proxies=self.proxies
            )
        except Exception as e:
            logger.error(f"Error occurred during {method} request to {url}. Exception: {e}")
            raise e

        if self.debug:
            logger.debug(f"Response: {r.status_code} {r.content}")

        # Parse response based on content-type
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise ex.DataException(f"Invalid JSON response: {r.content}")

            if data.get("error_type"):
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()

                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)

            if not data.get("status", False):
                logger.error(
                    f"Request error: {data['message']} | URL: {url} | Params: {params} | Headers: {headers}"
                )

            return data

        elif "csv" in headers["Content-type"]:
            return r.content

        else:
            raise ex.DataException(
                f"Unknown Content-type ({headers['Content-type']}) with response: {r.content}"
            )


    def _deleteRequest(self, route: str, params: dict = None) -> dict | bytes:
        """
        Alias for sending a DELETE request.
        """
        return self._request(route, "DELETE", params)


    def _putRequest(self, route: str, params: dict = None) -> dict | bytes:
        """
        Alias for sending a PUT request.
        """
        return self._request(route, "PUT", params)


    def _postRequest(self, route: str, params: dict = None) -> dict | bytes:
        """
        Alias for sending a POST request.
        """
        return self._request(route, "POST", params)


    def _getRequest(self, route: str, params: dict = None) -> dict | bytes:
        """
        Alias for sending a GET request.
        """
        return self._request(route, "GET", params)


    def generateSession(self, clientCode: str, password: str, totp: str) -> dict:
        """
        Log in to the SmartAPI platform and generate session tokens.

        This method authenticates a user using their `clientCode`, `password`, and `TOTP` (Time-based One-Time Password).
        On successful login, it sets access token, refresh token, feed token, and user ID within the session.
        
        It also retrieves the user profile and adds authentication tokens to the returned user object.

        Args:
            clientCode (str): The user's client code.
            password (str): The password for the client code.
            totp (str): The time-based OTP for 2FA.

        Returns:
            dict: A dictionary containing user profile information and tokens if login is successful.
                If login fails, returns the error response from the API.
        """
        
        params = {
            "clientcode": clientCode,
            "password": password,
            "totp": totp
        }

        loginResultObject = self._postRequest("api.login", params)

        if loginResultObject['status'] is True:
            jwtToken = loginResultObject['data']['jwtToken']
            refreshToken = loginResultObject['data']['refreshToken']
            feedToken = loginResultObject['data']['feedToken']

            self.setAccessToken(jwtToken)
            self.setRefreshToken(refreshToken)
            self.setFeedToken(feedToken)

            user = self.getProfile(refreshToken)
            userId = user['data']['clientcode']
            self.setUserId(userId)

            # Enrich user response with auth tokens
            user['data']['jwtToken'] = f"Bearer {jwtToken}"
            user['data']['refreshToken'] = refreshToken
            user['data']['feedToken'] = feedToken

            return user
        else:
            return loginResultObject


    def terminateSession(self, clientCode: str) -> dict:
        """
        Log out the current user session.
        """
        return self._postRequest("api.logout", {"clientcode": clientCode})


    def generateToken(self, refresh_token: str) -> dict:
        """
        Regenerate JWT and feed tokens.
        """
        response = self._postRequest(
            "api.token", {"refreshToken": refresh_token}
        )
        jwtToken = response['data']['jwtToken']
        feedToken = response['data']['feedToken']

        self.setFeedToken(feedToken)
        self.setAccessToken(jwtToken)

        return response

    def renewAccessToken(self) -> dict:
        """
        Renew access token using refresh token.
        """
        response = self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token,
        })

        tokenSet = {}
        if "jwtToken" in response:
            tokenSet['jwtToken'] = response['data']['jwtToken']
        tokenSet['clientcode'] = self.userId
        tokenSet['refreshToken'] = response['data']["refreshToken"]
        
        return tokenSet

    def getProfile(self, refreshToken: str) -> dict:
        """
        Fetch user profile using refresh token.
        """
        return self._getRequest("api.user.profile", {"refreshToken": refreshToken})


    def placeOrder(self, orderparams: dict) -> str | None:
        """
        Place an order and return order ID.
        """
        params = {k: v for k, v in orderparams.items() if v is not None}
        response = self._postRequest("api.order.place", params)
        
        if response and response.get('status', False):
            if 'data' in response and response['data'] and 'orderid' in response['data']:
                return response['data']['orderid']
            logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
        return None


    def placeOrderFullResponse(self, orderparams: dict) -> dict:
        """
        Place order and return full API response.
        """
        params = {k: v for k, v in orderparams.items() if v is not None}
        response = self._postRequest("api.order.placefullresponse", params)
        
        if response and response.get('status', False):
            if 'data' in response and response['data'] and 'orderid' in response['data']:
                return response
            logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
            
        return response


    def modifyOrder(self, orderparams: dict) -> dict:
        """
        Modify an existing order.
        """
        params = {k: v for k, v in orderparams.items() if v is not None}
        return self._postRequest("api.order.modify", params)


    def cancelOrder(self, order_id: str, variety: str) -> dict:
        """
        Cancel an order by ID and variety.
        """
        return self._postRequest("api.order.cancel", {"variety": variety, "orderid": order_id})


    def ltpData(
        self, 
        exchange: str, 
        tradingsymbol: str, 
        symboltoken: str
    ) -> dict:
        """
        Retrieve the latest traded price (LTP) data for a given symbol.

        Args:
            exchange (str): The exchange code (e.g., NSE, BSE).
            tradingsymbol (str): The trading symbol of the security.
            symboltoken (str): The unique token identifier for the symbol.

        Returns:
            dict: The response containing LTP data.
        """
        params = {
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken
        }
        return self._postRequest("api.ltp.data", params)


    def orderBook(self) -> dict:
        """
        Fetch the current order book.
        """
        return self._getRequest("api.order.book")

    def tradeBook(self) -> dict:
        """
        Fetch the current trade book.
        """
        return self._getRequest("api.trade.book")

    def rmsLimit(self) -> dict:
        """
        Fetch user's RMS limit details.
        """
        return self._getRequest("api.rms.limit")

    def position(self) -> dict:
        """
        Fetch user's open positions.
        """
        return self._getRequest("api.position")

    def holding(self) -> dict:
        """
        Fetch user's current holdings.
        """
        return self._getRequest("api.holding")

    def allholding(self) -> dict:
        """
        Fetch all holdings including T1.
        """
        return self._getRequest("api.allholding")


    def convertPosition(self, positionParams: dict) -> dict:
        """
        Convert open positions.
        """
        params = {k: v for k, v in positionParams.items() if v is not None}
        return self._postRequest("api.convert.position", params)


    def gttCreateRule(self, createRuleParams: dict) -> str:
        """
        Create a new GTT rule.
        """
        params = {k: v for k, v in createRuleParams.items() if v is not None}
        response = self._postRequest("api.gtt.create", params)
        return response['data']['id']


    def gttModifyRule(self, modifyRuleParams: dict) -> str:
        """
        Modify an existing GTT rule.
        """
        params = {k: v for k, v in modifyRuleParams.items() if v is not None}
        response = self._postRequest("api.gtt.modify", params)
        return response['data']['id']


    def gttCancelRule(self, gttCancelParams: dict) -> dict:
        """
        Cancel a GTT rule.
        """
        params = {k: v for k, v in gttCancelParams.items() if v is not None}
        return self._postRequest("api.gtt.cancel", params)


    def gttDetails(self, id: str) -> dict:
        """
        Fetch details of a GTT rule.
        """
        return self._postRequest("api.gtt.details", {"id": id})


    def gttLists(self, status: list, page: int, count: int) -> dict | str:
        """
        List GTT rules by status.
        """
        if isinstance(status, list):
            params = {"status": status, "page": page, "count": count}
            return self._postRequest("api.gtt.list", params)
        
        return (
            f"The status param is {type(status)}. "
            f"Please use a list like status=['CANCELLED']"
        )


    def getCandleData(self, historicDataParams: dict) -> dict:
        """
        Fetch historical candlestick data for a given symbol and time range.

        Args:
            historicDataParams (dict): Parameters for the request, including symbol, 
                                    interval, start and end time, etc.

        Returns:
            dict: The API response containing historical candle data.
        """
        params = {
            k: v for k, v in historicDataParams.items() if v is not None
        }
        return self._postRequest("api.candle.data", params)


    def getOIData(self, historicOIDataParams: dict) -> dict:
        """
        Fetch historical open interest data.
        """
        params = {k: v for k, v in historicOIDataParams.items() if v is not None}
        return self._postRequest("api.oi.data", params)

    def getMarketData(self, mode: str, exchangeTokens: dict) -> dict:
        """
        Get market data for given exchange tokens.
        """
        params = {
            "mode": mode,
            "exchangeTokens": exchangeTokens
        }
        return self._postRequest("api.market.data", params)

    def searchScrip(self, exchange: str, searchscrip: str) -> dict:
        """
        Search for a scrip in an exchange.
        """
        params = {
            "exchange": exchange,
            "searchscrip": searchscrip
        }
        result = self._postRequest("api.search.scrip", params)

        if result["status"] and result["data"]:
            message = f"Found {len(result['data'])} trading symbols:"
            symbols = "\n".join([
                f"{i + 1}. exchange: {item['exchange']}, "
                f"tradingsymbol: {item['tradingsymbol']}, "
                f"symboltoken: {item['symboltoken']}"
                for i, item in enumerate(result["data"])
            ])

            logger.info(message + "\n" + symbols)
        elif result["status"] and not result["data"]:
            logger.info("Search successful. No symbols found.")
        return result


    def make_authenticated_get_request(self, url: str, access_token: str) -> dict | None:
        """
        Make a GET request with auth header.
        """
        headers = self.requestHeaders()
        if access_token:
            headers["Authorization"] = "Bearer " + access_token
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        logger.error(f"GET request failed: {response.status_code}")
        return None


    def individual_order_details(self, qParam: str) -> dict | None:
        """
        Fetch details for an individual order.
        """
        url = ROOTURL + ROUTES["api.individual.order.details"] + qParam
        try:
            return self.make_authenticated_get_request(url, self.access_token)
        except Exception as e:
            logger.error(f"Error in individual_order_details: {e}")
            return None


    def getMarginApi(self, params: dict) -> dict:
        """
        Get margin info for user and symbols.
        """
        return self._postRequest("api.margin.api", params)

    def estimateCharges(self, params: dict) -> dict:
        """
        Estimate brokerage and tax charges.
        """
        return self._postRequest("api.estimateCharges", params)

    def verifyDis(self, params: dict) -> dict:
        """
        Verify DIS (depository instruction slip).
        """
        return self._postRequest("api.verifyDis", params)

    def generateTPIN(self, params: dict) -> dict:
        """
        Generate TPIN for DIS authorization.
        """
        return self._postRequest("api.generateTPIN", params)

    def getTranStatus(self, params: dict) -> dict:
        """
        Check transaction status for EDIS.
        """
        return self._postRequest("api.getTranStatus", params)

    def optionGreek(self, params: dict) -> dict:
        """
        Fetch option greeks data.
        """
        return self._postRequest("api.optionGreek", params)

    def gainersLosers(self, params: dict) -> dict:
        """
        Get top gainers and losers.
        """
        return self._postRequest("api.gainersLosers", params)

    def putCallRatio(self) -> dict:
        """
        Get put-call ratio data.
        """
        return self._getRequest("api.putCallRatio")

    def nseIntraday(self) -> dict:
        """
        Fetch intraday data for NSE.
        """
        return self._getRequest("api.nseIntraday")

    def bseIntraday(self) -> dict:
        """
        Fetch intraday data for BSE.
        """
        return self._getRequest("api.bseIntraday")

    def oIBuildup(self, params: dict) -> dict:
        """
        Fetch Open Interest buildup data.
        """
        return self._postRequest("api.oIBuildup", params)

    def _user_agent(self) -> str:
        """
        Return custom user agent string.
        """
        return (__title__ + "-python/").capitalize() + __version__
