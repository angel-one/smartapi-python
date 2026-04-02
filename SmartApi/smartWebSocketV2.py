import struct
import time
import ssl
import json
from websocket import WebSocketApp

from SmartApi.loggerConfig import get_logger

logger = get_logger(__name__, level="WARNING")


class SmartWebSocketV2(object):
    """
    SmartAPI Web Socket version 2

    This class manages a WebSocket connection to the SmartAPI 
    for real-time market data streaming. It supports subscription,
    message parsing, and automatic handling of control messages
    like ping/pong.
    """


    ROOT_URI = "wss://smartapisocket.angelone.in/smart-stream"
    HEART_BEAT_MESSAGE = "ping"
    HEART_BEAT_INTERVAL = 10  # Adjusted to 10s
    LITTLE_ENDIAN_BYTE_ORDER = "<"
    RESUBSCRIBE_FLAG = False
    # HB_THREAD_FLAG = True

    # Available Actions
    SUBSCRIBE_ACTION = 1
    UNSUBSCRIBE_ACTION = 0

    # Possible Subscription Mode
    LTP_MODE = 1
    QUOTE = 2
    SNAP_QUOTE = 3
    DEPTH = 4

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
        3: "SNAP_QUOTE",
        4: "DEPTH"
    }

    wsapp = None
    input_request_dict = {}
    current_retry_attempt = 0

    def __init__(
        self, 
        auth_token: str, 
        api_key: str, 
        client_code: str, 
        feed_token: str, 
        max_retry_attempt: int = 1,
        retry_strategy: int = 0, 
        retry_delay: int = 10, 
        retry_multiplier: int = 2, 
        retry_duration: int = 60
    ):
        """
        Initialize the SmartWebSocketV2 instance.

        This constructor sets up the WebSocket client with the necessary 
        credentials and retry configuration for establishing and maintaining 
        a connection with the Smart API's real-time data feed.

        Parameters
        ----------
        auth_token : str
            JWT authentication token received from the Smart API login endpoint.
        api_key : str
            Unique API key provided for accessing the Smart API.
        client_code : str
            Your Angel One client code (e.g., "D12345").
        feed_token : str
            Token required for subscribing to live market feeds.
        max_retry_attempt : int, optional
            Maximum number of reconnection attempts on failure (default is 1).
        retry_strategy : int, optional
            Strategy to use for retrying connections:
            - 0: Fixed delay
            - 1: Exponential backoff (default is 0).
        retry_delay : int, optional
            Base delay in seconds between retries (default is 10).
        retry_multiplier : int, optional
            Multiplier applied to delay in case of exponential backoff (default is 2).
        retry_duration : int, optional
            Total duration (in seconds) to attempt retries before giving up (default is 60).

        Returns
        -------
        None
            This constructor does not return a value.
        """

        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.DISCONNECT_FLAG = True
        self.last_pong_timestamp = None
        self.MAX_RETRY_ATTEMPT = max_retry_attempt
        self.retry_strategy = retry_strategy
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_duration = retry_duration        
        
        
        if not self._sanity_check():
            logger.error("Invalid initialization parameters. Provide valid values for all the tokens.")
            raise Exception("Provide valid value for all the tokens")
        
    def _sanity_check(self) -> bool:
        """
        Check if essential tokens and codes are present.
        """
        if not all([self.auth_token, self.api_key, self.client_code, self.feed_token]):
            return False
        return True

    def _on_message(self, wsapp: WebSocketApp, message: str):
        """
        Handle incoming WebSocket message.
        """
        logger.info(f"Received message: {message}")
        if message != "pong":
            parsed_message = self._parse_binary_data(message)
            if self._is_control_message(parsed_message):
                self._handle_control_message(parsed_message)
            else:
                self.on_data(wsapp, parsed_message)
        else:
            self.on_message(wsapp, message)


    def _is_control_message(self, parsed_message: dict) -> bool:
        """
        Determine if the message is a control message.
        """
        return "subscription_mode" not in parsed_message


    def _handle_control_message(self, parsed_message: dict):
        """
        Process control messages like ping/pong.
        """
        if parsed_message["subscription_mode"] == 0:
            self._on_pong(self.wsapp, "pong")
        elif parsed_message["subscription_mode"] == 1:
            self._on_ping(self.wsapp, "ping")
        if hasattr(self, 'on_control_message'):
            self.on_control_message(self.wsapp, parsed_message)


    def _on_data(
        self, 
        wsapp: WebSocketApp, 
        data: bytes, 
        data_type: int, 
        continue_flag
    ):
        """
        Handle data messages with specific type.
        """
        if data_type == 2:
            parsed_message = self._parse_binary_data(data)
            self.on_data(wsapp, parsed_message)

    def _on_open(self, wsapp: WebSocketApp):
        """
        Handle WebSocket open event.
        """
        if self.RESUBSCRIBE_FLAG:
            self.resubscribe()
        else:
            self.on_open(wsapp)

    def _on_pong(self, wsapp: WebSocketApp, data: str):
        """
        Handle pong message from server.
        """
        if data == self.HEART_BEAT_MESSAGE:
            timestamp = time.time()
            formatted_timestamp = time.strftime("%d-%m-%y %H:%M:%S", time.localtime(timestamp))
            logger.info(f"In on pong function ==> {data}, Timestamp: {formatted_timestamp}")
            self.last_pong_timestamp = timestamp

    def _on_ping(self, wsapp: WebSocketApp, data: str):
        """
        Handle ping message from server.
        """
        timestamp = time.time()
        formatted_timestamp = time.strftime("%d-%m-%y %H:%M:%S", time.localtime(timestamp))
        logger.info(f"In on ping function ==> {data}, Timestamp: {formatted_timestamp}")
        self.last_ping_timestamp = timestamp


    def subscribe(
        self, 
        correlation_id: str, 
        mode: int, 
        token_list: list[dict]
    ) -> None:
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
            if mode == 4:
                for token in token_list:
                        if token.get('exchangeType') != 1:
                            error_message = (
                                f"Invalid ExchangeType: {token.get('exchangeType')}. "
                                "Please check the exchange type and try again. "
                                "It supports only one exchange type."
                            )
                            logger.error(error_message)
                            raise ValueError(error_message)
            
            if self.input_request_dict.get(mode) is None:
                self.input_request_dict[mode] = {}

            for token in token_list:
                if token['exchangeType'] in self.input_request_dict[mode]:
                    self.input_request_dict[mode][token['exchangeType']].extend(token["tokens"])
                else:
                    self.input_request_dict[mode][token['exchangeType']] = token["tokens"]

            if mode == self.DEPTH:
                total_tokens = sum(len(token["tokens"]) for token in token_list)
                quota_limit = 50
                if total_tokens > quota_limit:
                    error_message = (
                        f"Quota exceeded: You can subscribe to a maximum of {quota_limit} "
                        "tokens only."
                    )
                    logger.error(error_message)
                    raise Exception(error_message)

            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True

        except Exception as e:
            logger.error(f"Error occurred during subscribe: {e}")
            raise e


    def unsubscribe(
        self, 
        correlation_id: str, 
        mode: int, 
        token_list: list[dict]
    ) -> None:
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
            self.input_request_dict.update(request_data)
            self.wsapp.send(json.dumps(request_data))
            self.RESUBSCRIBE_FLAG = True
        except Exception as e:
            logger.error(f"Error occurred during unsubscribe: {e}")
            raise e


    def resubscribe(self) -> None:
        """
        Resubscribe to all WebSocket streams
        Based on saved subscription requests.
        """
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
            logger.error(f"Error occurred during resubscribe: {e}")
            raise e


    def connect(self):
        """
        Make the web socket connection with the server
        """
        headers = {
            "Authorization": self.auth_token,
            "x-api-key": str(self.api_key),
            "x-client-code": str(self.client_code),
            "x-feed-token": str(self.feed_token)
        }

        try:
            self.wsapp = WebSocketApp(
                self.ROOT_URI,
                header=headers,
                on_open=self._on_open,
                on_error=self._on_error,
                on_close=self._on_close,
                on_data=self._on_data,
                on_ping=self._on_ping,
                on_pong=self._on_pong
            )
            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.HEART_BEAT_INTERVAL
            )
        except Exception as e:
            logger.error(f"Error occurred during WebSocket connection: {e}")
            raise e


    def close_connection(self):
        """
        Closes the connection
        """
        self.RESUBSCRIBE_FLAG = False
        self.DISCONNECT_FLAG = True
        if self.wsapp:
            self.wsapp.close()

    def _on_error(self, wsapp: WebSocketApp, error: Exception):
        """
        Handle WebSocket error events.
        """
        self.RESUBSCRIBE_FLAG = True
        if self.current_retry_attempt < self.MAX_RETRY_ATTEMPT:
            logger.warning(
                f"Attempting to resubscribe/reconnect (Attempt "
                f"{self.current_retry_attempt + 1})..."
            )
            self.current_retry_attempt += 1
            
            if self.retry_strategy == 0: #retry_strategy for simple
                time.sleep(self.retry_delay)
            elif self.retry_strategy == 1: #retry_strategy for exponential
                delay = self.retry_delay * (self.retry_multiplier ** (self.current_retry_attempt - 1))
                time.sleep(delay)
            else:
                logger.error(f"Invalid retry strategy {self.retry_strategy}")
                raise Exception(f"Invalid retry strategy {self.retry_strategy}")
            
            try:
                self.close_connection()
                self.connect()
            except Exception as e:
                logger.error(f"Error occurred during resubscribe/reconnect: {e}")
                if hasattr(self, 'on_error'):
                    self.on_error("Reconnect Error", str(e) if str(e) else "Unknown error")
        else:
            self.close_connection()
            if hasattr(self, 'on_error'):
                self.on_error("Max retry attempt reached", "Connection closed")
                
            if self.retry_duration is not None and (
                self.last_pong_timestamp is not None and \
                time.time() - self.last_pong_timestamp > self.retry_duration * 60
            ):
                logger.warning("Connection closed due to inactivity.")
            else:
                logger.warning(
                    "Connection closed due to max retry attempts reached."
                )

    def _on_close(self, wsapp: WebSocketApp) -> None:
        """
        Handle WebSocket close event.
        """
        self.on_close(wsapp)


    def _parse_binary_data(self, binary_data: bytes) -> dict:
        parsed_data = {
            "subscription_mode": self._unpack_data(binary_data, 0, 1, byte_format="B")[0],
            "exchange_type": self._unpack_data(binary_data, 1, 2, byte_format="B")[0],
            "token": SmartWebSocketV2._parse_token_value(binary_data[2:27]),
            "sequence_number": self._unpack_data(binary_data, 27, 35, byte_format="q")[0],
            "exchange_timestamp": self._unpack_data(binary_data, 35, 43, byte_format="q")[0],
            "last_traded_price": self._unpack_data(binary_data, 43, 51, byte_format="q")[0]
        }

        try:
            sub_mode = parsed_data["subscription_mode"]
            parsed_data["subscription_mode_val"] = self.SUBSCRIPTION_MODE_MAP.get(sub_mode)

            if sub_mode in [self.QUOTE, self.SNAP_QUOTE]:
                # Define offsets and formats in a list of tuples for cleaner unpacking
                fields = [
                    ("last_traded_quantity", 51, 59, "q"),
                    ("average_traded_price", 59, 67, "q"),
                    ("volume_trade_for_the_day", 67, 75, "q"),
                    ("total_buy_quantity", 75, 83, "d"),
                    ("total_sell_quantity", 83, 91, "d"),
                    ("open_price_of_the_day", 91, 99, "q"),
                    ("high_price_of_the_day", 99, 107, "q"),
                    ("low_price_of_the_day", 107, 115, "q"),
                    ("closed_price", 115, 123, "q"),
                ]
                for field, start, end, fmt in fields:
                    parsed_data[field] = self._unpack_data(binary_data, start, end, byte_format=fmt)[0]

            if sub_mode == self.SNAP_QUOTE:
                snap_fields = [
                    ("last_traded_timestamp", 123, 131, "q"),
                    ("open_interest", 131, 139, "q"),
                    ("open_interest_change_percentage", 139, 147, "q"),
                    ("upper_circuit_limit", 347, 355, "q"),
                    ("lower_circuit_limit", 355, 363, "q"),
                    ("52_week_high_price", 363, 371, "q"),
                    ("52_week_low_price", 371, 379, "q"),
                ]
                for field, start, end, fmt in snap_fields:
                    parsed_data[field] = self._unpack_data(binary_data, start, end, byte_format=fmt)[0]

                best_5_buy_and_sell_data = self._parse_best_5_buy_and_sell_data(binary_data[147:347])
                # Fix swapped assignment (seems like a bug in original)
                parsed_data["best_5_buy_data"] = best_5_buy_and_sell_data["best_5_buy_data"]
                parsed_data["best_5_sell_data"] = best_5_buy_and_sell_data["best_5_sell_data"]

            if sub_mode == self.DEPTH:
                # Remove irrelevant keys
                for key in ["sequence_number", "last_traded_price", "subscription_mode_val"]:
                    parsed_data.pop(key, None)

                parsed_data["packet_received_time"] = self._unpack_data(binary_data, 35, 43, byte_format="q")[0]
                depth_20_data = self._parse_depth_20_buy_and_sell_data(binary_data[43:])
                parsed_data["depth_20_buy_data"] = depth_20_data["depth_20_buy_data"]
                parsed_data["depth_20_sell_data"] = depth_20_data["depth_20_sell_data"]

            return parsed_data
        except Exception as e:
            logger.error(f"Error occurred during binary data parsing: {e}")
            raise e

    def _unpack_data(
        self, 
        binary_data: bytes, 
        start: int, 
        end: int, 
        byte_format: str = "I"
    ) -> tuple:
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


    def _parse_best_5_buy_and_sell_data(self, binary_data: bytes) -> dict:
        """
        Parse binary data to extract top 5 buy and sell order details.
        """
        def split_packets(binary_packets: bytes) -> list[bytes]:
            return [binary_packets[i:i + 20] for i in range(0, len(binary_packets), 20)]

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


    def _parse_depth_20_buy_and_sell_data(self, binary_data: bytes) -> dict:
        """
        Parse binary data to extract depth data for top 20 buy and sell orders.
        """
        depth_20_buy_data = []
        depth_20_sell_data = []

        for i in range(20):
            buy_start_idx = i * 10
            sell_start_idx = 200 + i * 10

            buy_packet_data = {
                "quantity": self._unpack_data(binary_data, buy_start_idx, buy_start_idx + 4, byte_format="i")[0],
                "price": self._unpack_data(binary_data, buy_start_idx + 4, buy_start_idx + 8, byte_format="i")[0],
                "num_of_orders": self._unpack_data(binary_data, buy_start_idx + 8, buy_start_idx + 10, byte_format="h")[0],
            }

            sell_packet_data = {
                "quantity": self._unpack_data(binary_data, sell_start_idx, sell_start_idx + 4, byte_format="i")[0],
                "price": self._unpack_data(binary_data, sell_start_idx + 4, sell_start_idx + 8, byte_format="i")[0],
                "num_of_orders": self._unpack_data(binary_data, sell_start_idx + 8, sell_start_idx + 10, byte_format="h")[0],
            }

            depth_20_buy_data.append(buy_packet_data)
            depth_20_sell_data.append(sell_packet_data)

        return {
            "depth_20_buy_data": depth_20_buy_data,
            "depth_20_sell_data": depth_20_sell_data
        }


    def on_message(self, wsapp: WebSocketApp, message: dict) -> None:
        """
        Handle incoming text messages from the WebSocket server.

        Parameters:
            wsapp (WebSocketApp): The WebSocket application instance.
            message (dict): The message payload received from the server.
        """
        pass

    def on_data(self, wsapp: WebSocketApp, data: dict) -> None:
        """
        Handle incoming binary data from the WebSocket server.

        Parameters:
            wsapp (WebSocketApp): The WebSocket application instance.
            data (dict): The binary data payload received from the server.
        """
        pass

    def on_control_message(self, wsapp: WebSocketApp, message: dict) -> None:
        """
        Handle WebSocket control messages such as ping, pong, or close frames.

        Parameters:
            wsapp (WebSocketApp): The WebSocket application instance.
            message (dict): The control message received.
        """
        pass

    def on_close(self, wsapp: WebSocketApp) -> None:
        """
        Handle WebSocket connection closure.

        Parameters:
            wsapp (WebSocketApp): The WebSocket application instance.
        """
        pass

    def on_open(self, wsapp: WebSocketApp) -> None:
        """
        Handle WebSocket connection open event.

        Parameters:
            wsapp (WebSocketApp): The WebSocket application instance.
        """
        pass

    def on_error(self, error: Exception) -> None:
        """
        Handle any exceptions or errors raised during the WebSocket connection.

        Parameters:
            error (Exception): The exception instance containing error details.
        """
        pass
