from threading import Thread
import time
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
import logging

TOKEN_URL = "https://demo-api.invendor.com/connect/token"
POST_URL = "https://demo-api.invendor.com/api/GPSEntries"
logger = logging.getLogger(__name__)

class SwaggerSession(Thread):
    def __init__(self, buffer_file):
        self.__buffer = buffer_file
        self.__secret_id = "test-app"
        self.__secret = "388D45FA-B36B-4988-BA59-B187D329C207"
        self.__client = BackendApplicationClient(client_id=self.__secret_id)
        self.__session = OAuth2Session(client=self.__client)
        self.__connected = False
        self.__run_thread = False
        self.__stopped = False

        Thread.__init__(self)

    def __connect(self):
        self.__connected = False
        token = self.__session.fetch_token(token_url=TOKEN_URL, client_id=self.__secret_id, client_secret=self.__secret, timeout=10)
        logger.info(f"Got token: {token}")
        if bool(token):
            self.__connected = True
        
    def close(self):
        logger.info("Closing session")
        self.__run_thread = False
        timeout_s = 1
        while not self.__stopped:
            time.sleep(0.1)
            timeout_s -= 0.1
            if timeout_s == 0:
                break;

    def run(self):
        self.__run_thread = True
        logger.info("Start session thread")
        while self.__run_thread:
            try:
                if not self.__connected:
                    self.__connect()
                coordinates = self.__buffer.pop_entry()
                if coordinates != None:
                    resp = self.__session.post(url=POST_URL,json=coordinates.as_payload(), timeout=10)
                    logger.info(f"sent {coordinates.as_payload()}, response: {resp}")
            except (TokenExpiredError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, OSError, TimeoutError) as e:
                logger.error(f"Connection error {e=}, retrying...")
                self.__connected = False
        self.__session.close()
        self.__stopped = True
                        
            
            
