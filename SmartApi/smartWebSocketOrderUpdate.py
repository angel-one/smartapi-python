import ssl
import time

import websocket
from websocket import WebSocketApp

from SmartApi.loggerConfig import get_logger

logger = get_logger(__name__, level="WARNING")


class SmartWebSocketOrderUpdate:
    """
    WebSocket client for receiving real-time order updates.
    """

    WEBSOCKET_URI: str = "wss://tns.angelone.in/smart-order-update"
    HEARTBEAT_MESSAGE: str = "ping"  # Heartbeat message to maintain connection
    HEARTBEAT_INTERVAL_SECONDS: int = 10  # Interval for heartbeat messages
    MAX_CONNECTION_RETRY_ATTEMPTS: int = 2  # Max retry attempts for connection
    RETRY_DELAY_SECONDS: int = 10  # Delay between retry attempts

    wsapp = None  # WebSocket connection instance
    last_pong_timestamp = None  # Timestamp of last received pong message
    current_retry_attempt = 0  # Current retry attempt count

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str
    ):
        """
        Initialize SmartWebSocketOrderUpdate with credentials.

        Parameters
        ----------
        auth_token : str
            Bearer token for WebSocket authorization.
        api_key : str
            Smart API key.
        client_code : str
            Angel One client code (user ID).
        feed_token : str
            Feed token for order update WebSocket.
        """
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token

    def on_message(self, wsapp, message: dict):
        """
        Handle incoming WebSocket message.
        """
        logger.info("Received message: %s", message)

    def on_data(self, wsapp, message, data_type, continue_flag):
        """
        Handle incoming WebSocket data frame.
        """
        self.on_message(wsapp, message)

    def on_open(self, wsapp):
        """
        Handle WebSocket connection open event.
        """
        logger.info("Connection opened")

    def on_error(self, wsapp, error):
        """
        Handle WebSocket error event.
        """
        logger.error("Error: %s", error)

    def on_close(self, wsapp, close_status_code, close_msg):
        """
        Handle WebSocket connection close event."""
        logger.info("Connection closed")
        self.retry_connect()

    def on_ping(self, wsapp, data):
        """
        Handle WebSocket ping event.
        """
        timestamp = time.time()
        formatted_timestamp = time.strftime(
            "%d-%m-%y %H:%M:%S", time.localtime(timestamp)
        )
        logger.info(
            "In on ping function ==> %s, Timestamp: %s",
            data,
            formatted_timestamp
        )

    def on_pong(self, wsapp, data):
        """
        Handle WebSocket pong event.
        """
        if data == self.HEARTBEAT_MESSAGE:
            timestamp = time.time()
            formatted_timestamp = time.strftime(
                "%d-%m-%y %H:%M:%S", time.localtime(timestamp)
            )
            logger.info(
                "In on pong function ==> %s, Timestamp: %s", 
                data,
                formatted_timestamp
            )
            self.last_pong_timestamp = timestamp
        else:
            self.on_data(wsapp, data, websocket.ABNF.OPCODE_BINARY, False)

    def check_connection_status(self):
        """
        Check if connection is alive based on pong timestamp.
        """
        current_time = time.time()
        if (
            self.last_pong_timestamp is not None and
            current_time - self.last_pong_timestamp > 2 * self.HEARTBEAT_INTERVAL_SECONDS
        ):
            self.close_connection()

    def connect(self):
        """
        Establish the WebSocket connection.
        """
        headers = {
            "Authorization": self.auth_token,
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token
        }

        try:
            self.wsapp = WebSocketApp(
                self.WEBSOCKET_URI,
                header=headers,
                on_open=self.on_open,
                on_error=self.on_error,
                on_close=self.on_close,
                on_data=self.on_data,
                on_ping=self.on_ping,
                on_pong=self.on_pong
            )

            self.wsapp.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.HEARTBEAT_INTERVAL_SECONDS
            )
        except Exception as e:
            logger.error("Error connecting to WebSocket: %s", e)
            self.retry_connect()

    def retry_connect(self):
        """
        Attempt to reconnect on connection failure.
        """
        if self.current_retry_attempt < self.MAX_CONNECTION_RETRY_ATTEMPTS:
            logger.info(
                "Retrying connection (Attempt %s)...", 
                self.current_retry_attempt + 1
            )
            time.sleep(self.RETRY_DELAY_SECONDS)
            self.current_retry_attempt += 1
            self.connect()
        else:
            logger.warning("Max retry attempts reached.")

    def close_connection(self):
        """
        Close the WebSocket connection.
        """
        if self.wsapp:
            self.wsapp.close()
