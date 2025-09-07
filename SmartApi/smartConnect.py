from six.moves.urllib.parse import urljoin
import json
import logging
import SmartApi.smartExceptions as ex
import requests
from requests import get
import re, uuid
import socket
import os
import logzero
from logzero import logger
import time
import ssl
from SmartApi.version import __version__, __title__

log = logging.getLogger(__name__)

class SmartConnect(object):
    #_rootUrl = "https://openapisuat.angelbroking.com"
    _rootUrl="https://apiconnect.angelone.in" #prod endpoint
    #_login_url ="https://smartapi.angelbroking.com/login"
    _login_url="https://smartapi.angelone.in/publisher-login" #prod endpoint
    _default_timeout = 7  # In seconds

    _routes = {
        "api.login":"/rest/auth/angelbroking/user/v1/loginByPassword",
        "api.logout":"/rest/secure/angelbroking/user/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

        "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
        "api.order.placefullresponse": "/rest/secure/angelbroking/order/v1/placeOrder",
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

        "api.candle.data":"/rest/secure/angelbroking/historical/v1/getCandleData",
        "api.oi.data":"/rest/secure/angelbroking/historical/v1/getOIData",
        "api.market.data":"/rest/secure/angelbroking/market/v1/quote",
        "api.search.scrip": "/rest/secure/angelbroking/order/v1/searchScrip",
        "api.allholding": "/rest/secure/angelbroking/portfolio/v1/getAllHolding",

        "api.individual.order.details": "/rest/secure/angelbroking/order/v1/details/",
        "api.margin.api" : 'rest/secure/angelbroking/margin/v1/batch',
        "api.estimateCharges" : 'rest/secure/angelbroking/brokerage/v1/estimateCharges',
        "api.verifyDis" : 'rest/secure/angelbroking/edis/v1/verifyDis',
        "api.generateTPIN" : 'rest/secure/angelbroking/edis/v1/generateTPIN',
        "api.getTranStatus" : 'rest/secure/angelbroking/edis/v1/getTranStatus',
        "api.optionGreek" : 'rest/secure/angelbroking/marketData/v1/optionGreek',
        "api.gainersLosers" : 'rest/secure/angelbroking/marketData/v1/gainersLosers',
        "api.putCallRatio" : 'rest/secure/angelbroking/marketData/v1/putCallRatio',
        "api.oIBuildup" : 'rest/secure/angelbroking/marketData/v1/OIBuildup',
        "api.nseIntraday" : 'rest/secure/angelbroking/marketData/v1/nseIntraday',
        "api.bseIntraday" : 'rest/secure/angelbroking/marketData/v1/bseIntraday',
    }

    try:
        clientPublicIp= " " + get('https://api.ipify.org', timeout=5).text
        if " " in clientPublicIp:
            clientPublicIp=clientPublicIp.replace(" ","")
        hostname = socket.gethostname()
        clientLocalIp=socket.gethostbyname(hostname)
    except Exception as e:
        logger.error(f"Exception while retriving IP Address,using local host IP address: {e}")
    finally:
        clientPublicIp="106.193.147.98"
        clientLocalIp="127.0.0.1"
    clientMacAddress=':'.join(re.findall('..', '%012x' % uuid.getnode()))
    accept = "application/json"
    userType = "USER"
    sourceID = "WEB"

    def __init__(self, api_key=None, access_token=None, refresh_token=None,feed_token=None, userId=None, root=None, debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False,accept=None,userType=None,sourceID=None,Authorization=None,clientPublicIP=None,clientMacAddress=None,clientLocalIP=None,privateKey=None):
        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or self._rootUrl
        self.timeout = timeout or self._default_timeout
        self.Authorization= None
        self.clientLocalIP=self.clientLocalIp
        self.clientPublicIP=self.clientPublicIp
        self.clientMacAddress=self.clientMacAddress
        self.privateKey=api_key
        self.accept=self.accept
        self.userType=self.userType
        self.sourceID=self.sourceID

        # Create SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.options |= ssl.OP_NO_TLSv1  # Disable TLS 1.0
        self.ssl_context.options |= ssl.OP_NO_TLSv1_1  # Disable TLS 1.1

        # Configure minimum TLS version to TLS 1.2
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if not disable_ssl:
            self.reqsession = requests.Session()
            if pool is not None:
                reqadapter = requests.adapters.HTTPAdapter(**pool)
                self.reqsession.mount("https://", reqadapter)
            else:
                reqadapter = requests.adapters.HTTPAdapter()
                self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            # If SSL is disabled, use the default SSL context
            self.reqsession = requests
            
        # Create a log folder based on the current date
        log_folder = time.strftime("%Y-%m-%d", time.localtime())
        log_folder_path = os.path.join("logs", log_folder)  # Construct the full path to the log folder
        os.makedirs(log_folder_path, exist_ok=True) # Create the log folder if it doesn't exist
        log_path = os.path.join(log_folder_path, "app.log") # Construct the full path to the log file
        logzero.logfile(log_path, loglevel=logging.ERROR)  # Output logs to a date-wise log file

        if pool:
            self.reqsession = requests.Session()
            reqadapter = requests.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            self.reqsession = requests

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()
    def requestHeaders(self):
        return{
            "Content-type":self.accept,
            "X-ClientLocalIP": self.clientLocalIp,
            "X-ClientPublicIP": self.clientPublicIp,
            "X-MACAddress": self.clientMacAddress,
            "Accept": self.accept,
            "X-PrivateKey": self.privateKey,
            "X-UserType": self.userType,
            "X-SourceID": self.sourceID
        }

    def setSessionExpiryHook(self, method):
        if not callable(method):
            raise TypeError("Invalid input type. Only functions are accepted.")
        self.session_expiry_hook = method
    
    def getUserId():
        return userId

    def setUserId(self,id):
        self.userId=id

    def setAccessToken(self, access_token):

        self.access_token = access_token

    def setRefreshToken(self, refresh_token):

        self.refresh_token = refresh_token

    def setFeedToken(self,feedToken):
        
        self.feed_token=feedToken

    def getfeedToken(self):
        return self.feed_token

    
    def login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s" % (self._login_url, self.api_key)
    
    def _request(self, route, method, parameters=None):
        """Make an HTTP request."""
        params = parameters.copy() if parameters else {}
       
        uri =self._routes[route].format(**params)
        url = urljoin(self.root, uri)


        # Custom headers
        headers = self.requestHeaders()

        if self.access_token:
            # set authorization header
        
            auth_header = self.access_token
            headers["Authorization"] = "Bearer {}".format(auth_header)

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params, headers=headers))
    
        try:
            r = requests.request(method,
                                        url,
                                        data=json.dumps(params) if method in ["POST", "PUT"] else None,
                                        params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                                        headers=headers,
                                        verify=not self.disable_ssl,
                                        allow_redirects=True,
                                        timeout=self.timeout,
                                        proxies=self.proxies)
           
        except Exception as e:
            logger.error(f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
             
            except ValueError:
                raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            # api error
            if data.get("error_type"):
                # Call session hook if its registered and TokenException is raised
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()

                # native errors
                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)
            if data.get("status",False) is False : 
                logger.error(f"Error occurred while making a {method} request to {url}. Error: {data['message']}. URL: {url}, Headers: {self.requestHeaders()}, Request: {params}, Response: {data}")
            return data
        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ex.DataException("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))
        
    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)
    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)
    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)
    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def generateSession(self,clientCode,password,totp):
        
        params={"clientcode":clientCode,"password":password,"totp":totp}
        loginResultObject=self._postRequest("api.login",params)
        
        if loginResultObject['status']==True:
            jwtToken=loginResultObject['data']['jwtToken']
            self.setAccessToken(jwtToken)
            refreshToken = loginResultObject['data']['refreshToken']
            feedToken = loginResultObject['data']['feedToken']
            self.setRefreshToken(refreshToken)
            self.setFeedToken(feedToken)
            user = self.getProfile(refreshToken)

            id = user['data']['clientcode']
            # id='D88311'
            self.setUserId(id)
            user['data']['jwtToken'] = "Bearer " + jwtToken
            user['data']['refreshToken'] = refreshToken
            user['data']['feedToken'] = feedToken

            return user
        else:
            return loginResultObject
            
    def terminateSession(self,clientCode):
        logoutResponseObject=self._postRequest("api.logout",{"clientcode":clientCode})
        return logoutResponseObject

    def generateToken(self,refresh_token):
        response=self._postRequest('api.token',{"refreshToken":refresh_token})
        jwtToken=response['data']['jwtToken']
        feedToken=response['data']['feedToken']
        self.setFeedToken(feedToken)
        self.setAccessToken(jwtToken)

        return response

    def renewAccessToken(self):
        response =self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token,
            
        })
       
        tokenSet={}

        if "jwtToken" in response:
            tokenSet['jwtToken']=response['data']['jwtToken']
        tokenSet['clientcode']=self. userId   
        tokenSet['refreshToken']=response['data']["refreshToken"]
       
        return tokenSet

    def getProfile(self,refreshToken):
        user=self._getRequest("api.user.profile",{"refreshToken":refreshToken})
        return user

    def placeOrder(self,orderparams):
        params=orderparams
        for k in list(params.keys()):
            if params[k] is None :
                del(params[k])
        response= self._postRequest("api.order.place", params)
        if response is not None and response.get('status', False):
            if 'data' in response and response['data'] is not None and 'orderid' in response['data']:
                orderResponse = response['data']['orderid']
                return orderResponse
            else:
                logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
        return None

    def placeOrderFullResponse(self,orderparams):
        params=orderparams
        for k in list(params.keys()):
            if params[k] is None :
                del(params[k])
        response= self._postRequest("api.order.placefullresponse", params)
        if response is not None and response.get('status', False):
            if 'data' in response and response['data'] is not None and 'orderid' in response['data']:
                orderResponse = response
                return orderResponse
            else:
                logger.error(f"Invalid response format: {response}")
        else:
            logger.error(f"API request failed: {response}")
        return response
    
    def modifyOrder(self,orderparams):
        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])

        orderResponse= self._postRequest("api.order.modify", params)
        return orderResponse
    
    def cancelOrder(self, order_id,variety):
        orderResponse= self._postRequest("api.order.cancel", {"variety": variety,"orderid": order_id})
        return orderResponse

    def ltpData(self,exchange,tradingsymbol,symboltoken):
        params={
            "exchange":exchange,
            "tradingsymbol":tradingsymbol,
            "symboltoken":symboltoken
        }
        ltpDataResponse= self._postRequest("api.ltp.data",params)
        return ltpDataResponse
    
    def orderBook(self):
        orderBookResponse=self._getRequest("api.order.book")
        return orderBookResponse
        

    def tradeBook(self):
        tradeBookResponse=self._getRequest("api.trade.book")
        return tradeBookResponse
    
    def rmsLimit(self):
        rmsLimitResponse= self._getRequest("api.rms.limit")
        return rmsLimitResponse
    
    def position(self):
        positionResponse= self._getRequest("api.position")
        return positionResponse

    def holding(self):
        holdingResponse= self._getRequest("api.holding")
        return holdingResponse
    
    def allholding(self):
        allholdingResponse= self._getRequest("api.allholding")
        return allholdingResponse
    
    def convertPosition(self,positionParams):
        params=positionParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        convertPositionResponse= self._postRequest("api.convert.position",params)

        return convertPositionResponse

    def gttCreateRule(self,createRuleParams):
        params=createRuleParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])

        createGttRuleResponse=self._postRequest("api.gtt.create",params)
        return createGttRuleResponse['data']['id']

    def gttModifyRule(self,modifyRuleParams):
        params=modifyRuleParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        modifyGttRuleResponse=self._postRequest("api.gtt.modify",params)
        return modifyGttRuleResponse['data']['id']
     
    def gttCancelRule(self,gttCancelParams):
        params=gttCancelParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        cancelGttRuleResponse=self._postRequest("api.gtt.cancel",params)
        return cancelGttRuleResponse
     
    def gttDetails(self,id):
        params={
            "id":id
            }
        gttDetailsResponse=self._postRequest("api.gtt.details",params)
        return gttDetailsResponse
    
    def gttLists(self,status,page,count):
        if type(status)== list:
            params={
                "status":status,
                "page":page,
                "count":count
            }
            gttListResponse=self._postRequest("api.gtt.list",params)
            return gttListResponse
        else:
            message="The status param is entered as" +str(type(status))+". Please enter status param as a list i.e., status=['CANCELLED']"
            return message

    def getCandleData(self,historicDataParams):
        params=historicDataParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        getCandleDataResponse=self._postRequest("api.candle.data",historicDataParams)
        return getCandleDataResponse
    
    def getOIData(self,historicOIDataParams):
        params=historicOIDataParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        getOIDataResponse=self._postRequest("api.oi.data",historicOIDataParams)
        return getOIDataResponse
    
    def getMarketData(self,mode,exchangeTokens):
        params={
            "mode":mode,
            "exchangeTokens":exchangeTokens
        }
        marketDataResult=self._postRequest("api.market.data",params)
        return marketDataResult
    
    def searchScrip(self, exchange, searchscrip):
        params = {
            "exchange": exchange,
            "searchscrip": searchscrip
        }
        searchScripResult = self._postRequest("api.search.scrip", params)
        if searchScripResult["status"] is True and searchScripResult["data"]:
            message = f"Search successful. Found {len(searchScripResult['data'])} trading symbols for the given query:"
            symbols = ""
            for index, item in enumerate(searchScripResult["data"], start=1):
                symbol_info = f"{index}. exchange: {item['exchange']}, tradingsymbol: {item['tradingsymbol']}, symboltoken: {item['symboltoken']}"
                symbols += "\n" + symbol_info
            logger.info(message + symbols)
            return searchScripResult
        elif searchScripResult["status"] is True and not searchScripResult["data"]:
            logger.info("Search successful. No matching trading symbols found for the given query.")
            return searchScripResult
        else:
            return searchScripResult
        
    def make_authenticated_get_request(self, url, access_token):
        headers = self.requestHeaders()
        if access_token:
            headers["Authorization"] = "Bearer " + access_token
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        else:
            logger.error(f"Error in make_authenticated_get_request: {response.status_code}")
            return None
            
    def individual_order_details(self, qParam):
        url = self._rootUrl + self._routes["api.individual.order.details"] + qParam
        try:
            response_data = self.make_authenticated_get_request(url, self.access_token)
            return response_data
        except Exception as e:
            logger.error(f"Error occurred in ind_order_details: {e}")
            return None
    
    def getMarginApi(self,params):
        marginApiResult=self._postRequest("api.margin.api",params)
        return marginApiResult
    
    def estimateCharges(self,params):
        estimateChargesResponse=self._postRequest("api.estimateCharges",params)
        return estimateChargesResponse
    
    def verifyDis(self,params):
        verifyDisResponse=self._postRequest("api.verifyDis",params)
        return verifyDisResponse
    
    def generateTPIN(self,params):
        generateTPINResponse=self._postRequest("api.generateTPIN",params)
        return generateTPINResponse
    
    def getTranStatus(self,params):
        getTranStatusResponse=self._postRequest("api.getTranStatus",params)
        return getTranStatusResponse
    
    def optionGreek(self,params):
        optionGreekResponse=self._postRequest("api.optionGreek",params)
        return optionGreekResponse
    
    def gainersLosers(self,params):
        gainersLosersResponse=self._postRequest("api.gainersLosers",params)
        return gainersLosersResponse
    
    def putCallRatio(self):
        putCallRatioResponse=self._getRequest("api.putCallRatio")
        return putCallRatioResponse

    def nseIntraday(self):
        nseIntraday=self._getRequest("api.nseIntraday")
        return nseIntraday
    
    def bseIntraday(self):
        bseIntraday=self._getRequest("api.bseIntraday")
        return bseIntraday

    def oIBuildup(self,params):
        oIBuildupResponse=self._postRequest("api.oIBuildup",params)
        return oIBuildupResponse
    
   
    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__   

