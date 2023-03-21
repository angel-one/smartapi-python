from six.moves.urllib.parse import urljoin
import sys
import csv
import json
import dateutil.parser
import hashlib
import logging
import datetime
import SmartApi.smartExceptions as ex
import requests
from requests import get
import re, uuid
import socket
import platform
from SmartApi.version import __version__, __title__
from SmartApi import CONSTANTS
from logzero import logger



log = logging.getLogger(__name__)

class SmartConnect(object):
    _rootUrl=CONSTANTS._rootUrl #prod endpoint
    _login_url=CONSTANTS._login_url #prod endpoint

    _default_timeout = CONSTANTS._default_timeout  # In seconds

    _routes = CONSTANTS._routes


    try:
        clientPublicIp= " " + get('https://api.ipify.org').text
        if " " in clientPublicIp:
            clientPublicIp=clientPublicIp.replace(" ","")
        hostname = socket.gethostname()
        clientLocalIp=socket.gethostbyname(hostname)
    except Exception as e:
        logger.error(f"Exception while retriving IP Address,using local host IP address",e)
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
            logger.error(f"Exception while HTTP Request",e)
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
             
            except ValueError:
                logger.error(f"Couldn't parse the JSON response received from the server: {content}".format(content=r.content))
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
            refreshToken=loginResultObject['data']['refreshToken']
            feedToken=loginResultObject['data']['feedToken']
            self.setRefreshToken(refreshToken)
            self.setFeedToken(feedToken)
            user=self.getProfile(refreshToken)
        
            id=user['data']['clientcode']
            #id='D88311'
            self.setUserId(id)
            user['data']['jwtToken']="Bearer "+jwtToken
            user['data']['refreshToken']=refreshToken

            
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
        
        orderResponse= self._postRequest("api.order.place", params)
    
        return orderResponse
    
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
        logger.info(createGttRuleResponse)       
        return createGttRuleResponse['data']['id']

    def gttModifyRule(self,modifyRuleParams):
        params=modifyRuleParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        modifyGttRuleResponse=self._postRequest("api.gtt.modify",params)
        logger.info(modifyGttRuleResponse)
        return modifyGttRuleResponse['data']['id']
     
    def gttCancelRule(self,gttCancelParams):
        params=gttCancelParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        
        logger.info(params)
        cancelGttRuleResponse=self._postRequest("api.gtt.cancel",params)
        logger.info(cancelGttRuleResponse)
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
            logger.info(gttListResponse)
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
        
    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__   

