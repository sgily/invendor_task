from threading import Thread
import time
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging

TOKEN_URL = "https://demo-api.invendor.com/connect/token"
POST_URL = "https://demo-api.invendor.com/api/GPSEntries"
logger = logging.getLogger(__name__)

class SwaggerSession(Thread):
    def __init__(self, data_list):
        self.data_buf = data_list
        self.client_id = "test-app"
        self.secret = "388D45FA-B36B-4988-BA59-B187D329C207"
        client = BackendApplicationClient(client_id=self.client_id)
        self.session = OAuth2Session(client=client)
        self.token = self.session.fetch_token(token_url=TOKEN_URL, client_id=self.client_id, client_secret=self.secret)
        logger.info(f"Got token: {self.token}")
        Thread.__init__(self)


    def run(self):
        logger.info("Start session thread")
        while True:
            if not bool(self.data_buf):
                time.sleep(0.5)
            else:
                data_entry = self.data_buf.popleft()
                payload = {'createdDateTime': data_entry[0],
                            'latitude': str(data_entry[1]),
                            'longitude': str(data_entry[2])}
                resp = self.session.post(url=POST_URL,json=payload)
                logger.info(f"sent {payload}, response: {resp}")
            
