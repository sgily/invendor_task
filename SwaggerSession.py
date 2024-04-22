from threading import Thread
import time
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
import logging
from BufferFile import BufferFile
from BufferFile import LockAcquireError

TOKEN_URL = "https://demo-api.invendor.com/connect/token"
POST_URL = "https://demo-api.invendor.com/api/GPSEntries"
logger = logging.getLogger(__name__)

class SwaggerSession(Thread):
    def __init__(self, buffer_file):
        self.buffer = buffer_file
        self.client_id = "test-app"
        self.secret = "388D45FA-B36B-4988-BA59-B187D329C207"
        client = BackendApplicationClient(client_id=self.client_id)
        self.session = OAuth2Session(client=client)
        self.token = self.session.fetch_token(token_url=TOKEN_URL, client_id=self.client_id, client_secret=self.secret)
        logger.info(f"Got token: {self.token}")
        Thread.__init__(self)


    def run(self):
        logger.info("Start session thread")
        payload = None
        retry = False
        while True:
                if self.buffer.is_empty():
                    time.sleep(0.1)
                else:
                    try:
                        if not retry:
                            payload = self.buffer.pop_entry().as_payload()
                    except LockAcquireError:
                        logger.error(f"Failed to acquire key")
                        continue
                    try:
                        resp = self.session.post(url=POST_URL,json=payload)
                    except TokenExpiredError:
                        logger.error(f"token expired, refreshing")
                        self.token = self.session.fetch_token(token_url=TOKEN_URL, client_id=self.client_id, client_secret=self.secret)
                        logger.info("Retrying failed request")
                        retry = True
                    except Exception as err:
                        logger.error(f" {err=}, {type(err)=}")
                        logger.info("Retrying failed request")
                        retry = True
                    else:
                        logger.info(f"sent {payload}, response: {resp}")
                        
            
            
