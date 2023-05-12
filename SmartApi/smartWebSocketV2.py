from __future__ import print_function

import struct
import ssl
import json

import websocket


class SmartWebSocketV2(object):
    """
    SmartAPI Web Socket version 2
    """

    ROOT_URI = "ws://mds.angelone.in/smart-stream"
    # ROOT_URI = "ws://smartapisocket.angelone.in/smart-stream"
    HEART_BEAT_MESSAGE = "ping"
    HEAR_BEAT_INTERVAL = 10
    HEART_BEAT_TIMEOUT = 3
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    RESUBSCRIBE_FLAG = False
    MAX_RETRY_ATTEMPT = 1
    CLOSE_CONNECTION  = False
    MAX_ACTIVE_CONNECTIONS = 1000

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

    EXCHANGE_VALIDATOR = {1,2,3,4,5,7,13}

    wsapp = None
    input_request_dict = {}
    current_retry_attempt = 0

    ERROR_MAPPING = {
        'E1001' : "Invalid Request Payload.",
        'E1002' : "Invalid Request. Subscription Limit Exceeded."
    }

    def requestValidator(self,request_data):
        mode = request_data["params"]['mode']
        tokenLists = request_data['params']['tokenList']
        if mode not in range(1,4):
            print("mode can be either 1,2, or 3.")
            return False
        for tokenList in tokenLists:
                if tokenList['exchangeType'] not in self.EXCHANGE_VALIDATOR:
                    print("Incorrect exchange.")
                    return False
                tokens = tokenList['tokens']
                for token in tokens:
                    if token is None:
                        print("Token cannot be empty.")
                        return False



    def __init__(self, client_code, feed_token):
        """
            Initialise the SmartWebSocketV2 instance
            Parameters
            ------
            client_code: string
                angel one account id
            feed_token: string
                feed token received from Login API
        """
        self.client_code = client_code
        self.feed_token = feed_token
        self.no_of_active_connections = 0

        if not self._sanity_check():
            raise Exception("Provide valid value for all the tokens")

    def _sanity_check(self):
        if self.feed_token is None:
            return False
        return True

    def _on_data(self, wsapp, data, data_type, continue_flag):

        if data_type == 2:
            parsed_message = self._parse_binary_data(data)
            self.on_data(wsapp, parsed_message)
        else:
            self.on_data(wsapp, data)

    def _on_open(self, wsapp):

        if self.RESUBSCRIBE_FLAG:
            self.resubscribe()
        else:
            self.RESUBSCRIBE_FLAG = True
            self.on_open(wsapp)

    def _on_pong(self, wsapp, data):
        print("In on pong function==> ", data)

    def _on_ping(self, wsapp, data):
        print("In on ping function==> ", data)

    def subscribe(self, correlation_id, mode, token_list):
        """
            This Function subscribe the price data for the given token
            Parameters
            ------
            correlation_id: string
                A 10 character alphanumeric ID client may provide which will be returned by the server in error response
                to indicate which request generated error response.
                Clients can use this optional ID for tracking purposes between request and corresponding error response.
            mode: integer
                It denotes the subscription type
                possible values -> 1, 2 and 3
                1 -> LTP
                2 -> Quote
                3 -> Snap Quote
            token_list: list of dict
                Sample Value ->
                    [
                        { "exchangeType": 1, "tokens": ["10626", "5290"]},
                        {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                    ]
                    exchangeType: integer
                    possible values ->
                        1 -> nse_cm
                        2 -> nse_fo
                        3 -> bse_cm
                        4 -> bse_fo
                        5 -> mcx_fo
                        7 -> ncx_fo
                        13 -> cde_fo
                    tokens: list of string
        """
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.SUBSCRIBE_ACTION,
                "params": {
                    "mode": mode,
                    "tokenList": token_list
                }
            }


            if self.requestValidator(request_data) == False:
                print(self.ERROR_MAPPING['E1001'])





            if self.input_request_dict.get(mode, None) is None:
                self.input_request_dict[mode] = {}

            for token in token_list:
                if token['exchangeType'] in self.input_request_dict[mode]:
                    self.input_request_dict[mode][token['exchangeType']].extend(token["tokens"])
                    self.no_of_active_connections+=len(token["tokens"])
                else:
                    self.input_request_dict[mode][token['exchangeType']] = token["tokens"]
                    self.no_of_active_connections+=len(token["tokens"])

            if self.no_of_active_connections > self.MAX_ACTIVE_CONNECTIONS:
                print(self.ERROR_MAPPING['E1002'])

            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True
        except Exception as e:
            raise e

    def unsubscribe(self, correlation_id, mode, token_list):
        """
            This function unsubscribe the data for given token
            Parameters
            ------
            correlation_id: string
                A 10 character alphanumeric ID client may provide which will be returned by the server in error response
                to indicate which request generated error response.
                Clients can use this optional ID for tracking purposes between request and corresponding error response.
            mode: integer
                It denotes the subscription type
                possible values -> 1, 2 and 3
                1 -> LTP
                2 -> Quote
                3 -> Snap Quote
            token_list: list of dict
                Sample Value ->
                    [
                        { "exchangeType": 1, "tokens": ["10626", "5290"]},
                        {"exchangeType": 5, "tokens": [ "234230", "234235", "234219"]}
                    ]
                    exchangeType: integer
                    possible values ->
                        1 -> nse_cm
                        2 -> nse_fo
                        3 -> bse_cm
                        4 -> bse_fo
                        5 -> mcx_fo
                        7 -> ncx_fo
                        13 -> cde_fo
                    tokens: list of string
        """
        try:
            request_data = {
                "correlationID": correlation_id,
                "action": self.UNSUBSCRIBE_ACTION,
                "params": {
                    "mode": mode,
                    "tokenList": token_list
                }
            }
            mode = request_data["params"]['mode']
            token_list = request_data["params"]["tokenList"]
            print(self.input_request_dict)
            for tokenList in token_list:
                exchangeType = tokenList['exchangeType']
                tokens = tokenList['tokens']
                i=0
                while i<len(tokens):
                    if tokens[i] not in self.input_request_dict[mode][exchangeType]:
                        tokens.remove(tokens[i])
                    else:
                        i+=1

            self.no_of_active_connections = self.no_of_active_connections - len(tokens)
            self.input_request_dict.update(request_data)
            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True
        except Exception as e:
            raise e

    def resubscribe(self):
        try:
            for key, val in self.input_request_dict.items():
                token_list = []
                for key1, val1 in val.items():
                    temp_data = {
                        'exchangeType': key1,
                        'tokens': val1
                    }
                    token_list.append(temp_data)
                request_data = {
                    "action": self.SUBSCRIBE_ACTION,
                    "params": {
                        "mode": key,
                        "tokenList": token_list
                    }
                }
                self.wsapp.send(json.dumps(request_data))
        except Exception as e:
            raise e


    def connect(self):
        """
            Make the web socket connection with the server
        """
        try:
            headers = {
                "x-client-code": self.client_code,
                "x-feed-token": self.feed_token
            }
            self.wsapp = websocket.WebSocketApp(self.ROOT_URI, header=headers, on_open=self._on_open,
                                                on_error=self._on_error, on_close=self._on_close, on_data=self._on_data,
                                                on_ping=self._on_ping, on_pong=self._on_pong)
            self.wsapp.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=self.HEAR_BEAT_INTERVAL,
                                   ping_payload=self.HEART_BEAT_MESSAGE,ping_timeout=self.HEART_BEAT_TIMEOUT)
            
        except Exception as e:
            raise e

    def close_connection(self):
        """
            Closes the connection
        """
        print("No of Active Connections are: ",self.no_of_active_connections)
        self.CLOSE_CONNECTION = True
        self.RESUBSCRIBE_FLAG = False
        self.wsapp.close()

    def _on_error(self, wsapp, error):
        self.HB_THREAD_FLAG = False
        self.RESUBSCRIBE_FLAG = True
        print(error)
        if self.current_retry_attempt < self.MAX_RETRY_ATTEMPT and not self.CLOSE_CONNECTION:
            print("Attempting to resubscribe/reconnect...")
            self.current_retry_attempt += 1
            self.connect()

    def _on_close(self, wsapp):
        self.on_close(wsapp)

    def _parse_binary_data(self, binary_data):
        try:
            parsed_data = {
                "subscription_mode": self._unpack_data(binary_data, 0, 1, byte_format="B")[0],
                "exchange_type": self._unpack_data(binary_data, 1, 2, byte_format="B")[0],
                "token": SmartWebSocketV2._parse_token_value(binary_data[2:27]),
                "sequence_number": self._unpack_data(binary_data, 27, 35, byte_format="q")[0],
                "exchange_timestamp": self._unpack_data(binary_data, 35, 43, byte_format="q")[0],
                "last_traded_price": self._unpack_data(binary_data, 43, 51, byte_format="q")[0]
            }

            parsed_data["subscription_mode_val"] = self.SUBSCRIPTION_MODE_MAP.get(parsed_data["subscription_mode"])

            if parsed_data["subscription_mode"] in [self.QUOTE, self.SNAP_QUOTE]:
                parsed_data["last_traded_quantity"] = self._unpack_data(binary_data, 51, 59, byte_format="q")[0]
                parsed_data["average_traded_price"] = self._unpack_data(binary_data, 59, 67, byte_format="q")[0]
                parsed_data["volume_trade_for_the_day"] = self._unpack_data(binary_data, 67, 75, byte_format="q")[0]
                parsed_data["total_buy_quantity"] = self._unpack_data(binary_data, 75, 83, byte_format="d")[0]
                parsed_data["total_sell_quantity"] = self._unpack_data(binary_data, 83, 91, byte_format="d")[0]
                parsed_data["open_price_of_the_day"] = self._unpack_data(binary_data, 91, 99, byte_format="q")[0]
                parsed_data["high_price_of_the_day"] = self._unpack_data(binary_data, 99, 107, byte_format="q")[0]
                parsed_data["low_price_of_the_day"] = self._unpack_data(binary_data, 107, 115, byte_format="q")[0]
                parsed_data["closed_price"] = self._unpack_data(binary_data, 115, 123, byte_format="q")[0]

            if parsed_data["subscription_mode"] == self.SNAP_QUOTE:
                parsed_data["last_traded_timestamp"] = self._unpack_data(binary_data, 123, 131, byte_format="q")[0]
                parsed_data["open_interest"] = self._unpack_data(binary_data, 131, 139, byte_format="q")[0]
                parsed_data["open_interest_change_percentage"] = \
                    self._unpack_data(binary_data, 139, 147, byte_format="q")[0]
                parsed_data["upper_circuit_limit"] = self._unpack_data(binary_data, 347, 355, byte_format="q")[0]
                parsed_data["lower_circuit_limit"] = self._unpack_data(binary_data, 355, 363, byte_format="q")[0]
                parsed_data["52_week_high_price"] = self._unpack_data(binary_data, 363, 371, byte_format="q")[0]
                parsed_data["52_week_low_price"] = self._unpack_data(binary_data, 371, 379, byte_format="q")[0]
                best_5_buy_and_sell_data = self._parse_best_5_buy_and_sell_data(binary_data[147:347])
                parsed_data["best_5_buy_data"] = best_5_buy_and_sell_data["best_5_buy_data"]
                parsed_data["best_5_sell_data"] = best_5_buy_and_sell_data["best_5_sell_data"]

            return parsed_data
        except Exception as e:
            raise e

    def _unpack_data(self, binary_data, start, end, byte_format="I"):
        """
            Unpack Binary Data to the integer according to the specified byte_format.
            This function returns the tuple
        """
        return struct.unpack(self.LITTLE_ENDIAN_BYTE_ORDER + byte_format, binary_data[start:end])

    @staticmethod
    def _parse_token_value(binary_packet):
        token = ""
        for i in range(len(binary_packet)):
            if chr(binary_packet[i]) == '\x00':
                return token
            token += chr(binary_packet[i])
        return token
   

    def _parse_best_5_buy_and_sell_data(self, binary_data):

        def split_packets(binary_packets):
            packets = []

            i = 0
            while i < len(binary_packets):
                packets.append(binary_packets[i: i+20])
                i += 20
            return packets

        best_5_buy_sell_packets = split_packets(binary_data)

        best_5_buy_data = []
        best_5_sell_data = []

        for packet in best_5_buy_sell_packets:
            each_data = {
                "flag": self._unpack_data(packet, 0, 2, byte_format="H")[0],
                "quantity": self._unpack_data(packet, 2, 10, byte_format="q")[0],
                "price": self._unpack_data(packet, 10, 18, byte_format="q")[0],
                "no of orders": self._unpack_data(packet, 18, 20, byte_format="H")[0]
            }

            if each_data["flag"] == 0:
                best_5_buy_data.append(each_data)
            else:
                best_5_sell_data.append(each_data)

        return {
            "best_5_buy_data": best_5_buy_data,
            "best_5_sell_data": best_5_sell_data
        }

    def on_data(self, wsapp, data):
        pass

    def on_close(self, wsapp):
        pass

    def on_open(self, wsapp):
        pass

    def on_error(self):
        pass