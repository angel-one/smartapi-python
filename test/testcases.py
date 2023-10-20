import unittest
import pyotp
import os
import sys
import time
from logzero import logger

root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_directory)

from SmartApi.smartConnect import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

class TestCases(unittest.TestCase):
    def setUp(self):
        self.api_key = 'Your Api Key'
        self.username = 'Your client code'
        self.pwd = 'Your pin'
        self.token = 'Your QR value'
        self.totp = pyotp.TOTP(self.token).now()
        self.smart_api = SmartConnect(self.api_key)
        self.data = self.smart_api.generateSession(self.username, self.pwd, self.totp)
        self.authToken = self.data['data']['jwtToken']
        self.feedToken = self.smart_api.getfeedToken()
        self.refreshToken = self.data['data']['refreshToken']

    def test_getProfile(self):
        getprofile = self.smart_api.getProfile(self.refreshToken)
        self.assertTrue("status" in getprofile)
        self.assertTrue("message" in getprofile)
        self.assertTrue("errorcode" in getprofile)
        self.assertTrue("data" in getprofile)
        time.sleep(1)
       
    
    def test_holding(self):
        holding=self.smart_api.holding()
        self.assertTrue("status" in holding)
        self.assertTrue("message" in holding)
        self.assertTrue("errorcode" in holding)
        self.assertTrue("data" in holding)
        time.sleep(1)


    def test_allholding(self):
        allholding=self.smart_api.allholding()
        self.assertTrue("status" in allholding)
        self.assertTrue("message" in allholding)
        self.assertTrue("errorcode" in allholding)
        self.assertTrue("data" in allholding)       
        time.sleep(1)

    def test_orderBook(self):
        orderbook=self.smart_api.orderBook()
        self.assertTrue("status" in orderbook)
        self.assertTrue("message" in orderbook)
        self.assertTrue("errorcode" in orderbook)
        self.assertTrue("data" in orderbook) 
        time.sleep(1)

    def test_tradeBook(self):
        tradebook=self.smart_api.tradeBook()
        self.assertTrue("status" in tradebook)
        self.assertTrue("message" in tradebook)
        self.assertTrue("errorcode" in tradebook)
        self.assertTrue("data" in tradebook) 
        time.sleep(1)

    def test_rmsLimit(self):
        rmslimit=self.smart_api.rmsLimit()
        self.assertTrue("status" in rmslimit)
        self.assertTrue("message" in rmslimit)
        self.assertTrue("errorcode" in rmslimit)
        self.assertTrue("data" in rmslimit) 
        time.sleep(1)

    def test_ltpdata(self):
        ltp=self.smart_api.ltpData("NSE", "SBIN-EQ", "3045")
        self.assertTrue("status" in ltp)
        self.assertTrue("message" in ltp)
        self.assertTrue("errorcode" in ltp)
        self.assertTrue("data" in ltp) 
        time.sleep(1)

    def test_searchScrip(self):
        exchange = "BSE"
        searchscrip = "Titan"
        searchScripData = self.smart_api.searchScrip(exchange, searchscrip)
        self.assertTrue("status" in searchScripData)
        self.assertTrue("message" in searchScripData)
        self.assertTrue("errorcode" in searchScripData)
        self.assertTrue("data" in searchScripData)
        time.sleep(1)

    def test_getMarketData(self):
        mode="FULL"
        exchangeTokens= {"NSE": ["3045"]}
        marketData=self.smart_api.getMarketData(mode, exchangeTokens)
        self.assertTrue("status" in marketData)
        self.assertTrue("message" in marketData)
        self.assertTrue("errorcode" in marketData)
        self.assertTrue("data" in marketData)
        time.sleep(1)

    def test_getCandleData(self):
        candleParams = {
            "exchange": "NSE",
            "symboltoken": "3045",
            "interval": "FIVE_MINUTE",
            "fromdate": "2023-10-18 09:15",
            "todate": "2023-10-18 09:20"
        }
        candledetails = self.smart_api.getCandleData(candleParams)
        self.assertTrue("status" in candledetails)
        self.assertTrue("message" in candledetails)
        self.assertTrue("errorcode" in candledetails)
        self.assertTrue("data" in candledetails)
        time.sleep(1)
    
    def test_position(self):
        pos=self.smart_api.position()
        self.assertTrue("status" in pos)
        self.assertTrue("message" in pos)
        self.assertTrue("errorcode" in pos)
        self.assertTrue("data" in pos)
        time.sleep(1)

    def test_convertPosition(self):
        params = {
            "exchange": "NSE",
            "oldproducttype": "DELIVERY",
            "newproducttype": "MARGIN",
            "tradingsymbol": "SBIN-EQ",
            "transactiontype": "BUY",
            "quantity": 1,
            "type": "DAY"
            }
        convertposition=self.smart_api.convertPosition(params)
        self.assertTrue("status" in convertposition)
        self.assertTrue("message" in convertposition)
        self.assertTrue("errorcode" in convertposition)
        self.assertTrue("data" in convertposition)
        time.sleep(1)
    
    def test_gtt_create_modify_cancel_details_rule(self):
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
        rule_id = self.smart_api.gttCreateRule(gttCreateParams)
        self.assertTrue(rule_id, "gttCreateRule request failed...")

        gttModifyParams = {
                "id": rule_id,
                "symboltoken": "3045",
                "exchange": "NSE",
                "price": 19500,
                "quantity": 10,
                "triggerprice": 200000,
                "disclosedqty": 10,
                "timeperiod": 365
            }
        modified_id = self.smart_api.gttModifyRule(gttModifyParams)
        self.assertTrue(modified_id, "gttModifyRule request failed...")
        self.assertEqual(rule_id, modified_id)

        cancelParams = {
                "id": rule_id,
                "symboltoken": "3045",
                "exchange": "NSE"
            }

        cancelled_id = self.smart_api.gttCancelRule(cancelParams)
        self.assertTrue("status" in cancelled_id)
        self.assertTrue("message" in cancelled_id)
        self.assertTrue("errorcode" in cancelled_id)
        self.assertTrue("data" in cancelled_id)

        gttdetails=self.smart_api.gttDetails(rule_id)
        self.assertTrue("status" in gttdetails)
        self.assertTrue("message" in gttdetails)
        self.assertTrue("errorcode" in gttdetails)
        self.assertTrue("data" in gttdetails)
        time.sleep(1)

    def test_gttLists(self):
        page = '1'  
        count = '5'  
        status=['CANCELLED']
        gtt_lists = self.smart_api.gttLists(status, page, count)
        self.assertTrue("status" in gtt_lists)
        self.assertTrue("message" in gtt_lists)
        self.assertTrue("errorcode" in gtt_lists)
        self.assertTrue("data" in gtt_lists)
        time.sleep(1)
    
    def test_place_modify_cancel_order(self):
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
        orderid = self.smart_api.placeOrder(orderparams)
        self.assertTrue(orderid, "placeorder request failed...")

        modifyparams = {
            "variety": "NORMAL",
            "orderid": orderid,
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "19500",
            "quantity": "1",
            "tradingsymbol": "SBIN-EQ",
            "symboltoken": "3045",
            "exchange": "NSE"
        }
        modifyparams=self.smart_api.modifyOrder(modifyparams)
        self.assertTrue("status" in modifyparams)
        self.assertTrue("message" in modifyparams)
        self.assertTrue("errorcode" in modifyparams)
        self.assertTrue("data" in modifyparams)
    
        cancleorder=self.smart_api.cancelOrder(orderid, "NORMAL")
        self.assertTrue("status" in cancleorder)
        self.assertTrue("message" in cancleorder)
        self.assertTrue("errorcode" in cancleorder)
        self.assertTrue("data" in cancleorder)
        time.sleep(1)

    def test_websocket_connection(self):
        AUTH_TOKEN = self.authToken
        API_KEY = self.api_key
        CLIENT_CODE = self.username
        FEED_TOKEN = self.feedToken
        correlation_id = "abcde12345"
        action = 1
        mode = 4
        exchangeType = 1
        token_list = [
            {
                "action": action,
                "exchangeType": exchangeType,
                "tokens": ["3045"]
            }
        ]

        sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

        def on_data(wsapp, message):
            # logger.info("Ticks: {}".format(message))
            close_connection()

        def on_open(wsapp):
            logger.info("on open")
            sws.subscribe(correlation_id, mode, token_list)

        def on_error(wsapp, error):
            logger.error(error)

        def on_close(wsapp):
            logger.info("Close")
            close_connection()

        def close_connection():
            sws.close_connection()
        # Assign the callbacks.
        sws.on_open = on_open
        sws.on_data = on_data
        sws.on_error = on_error
        sws.on_close = on_close
        sws.connect()
        time.sleep(1)

    def test_terminateSession(self):
        terminate = self.smart_api.terminateSession('Your User Name')
        self.assertTrue("status" in terminate)
        self.assertTrue("message" in terminate)
        self.assertTrue("errorcode" in terminate)
        self.assertTrue("data" in terminate)
        time.sleep(1)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestCases('test_getProfile'))
    suite.addTest(TestCases('test_holding'))
    suite.addTest(TestCases('test_allholding'))
    suite.addTest(TestCases('test_orderBook'))
    suite.addTest(TestCases('test_tradeBook'))
    suite.addTest(TestCases('test_rmsLimit'))
    suite.addTest(TestCases('test_ltpdata'))
    suite.addTest(TestCases('test_searchScrip'))
    suite.addTest(TestCases('test_getMarketData'))
    suite.addTest(TestCases('test_getCandleData'))
    suite.addTest(TestCases('test_position'))
    suite.addTest(TestCases('test_convertPosition'))
    suite.addTest(TestCases('test_gtt_create_modify_cancel_details_rule'))
    suite.addTest(TestCases('test_gttLists'))
    suite.addTest(TestCases('test_place_modify_cancel_order'))
    suite.addTest(TestCases('test_websocket_connection'))
    suite.addTest(TestCases('test_terminateSession'))
    unittest.TextTestRunner(verbosity=2).run(suite)

