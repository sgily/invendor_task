
import socket
import struct
import collections
from datetime import datetime,timezone
from SwaggerSession import SwaggerSession
import logging

HOST = "gpshost"  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on (non-privileged ports are > 1023)
rbuf = collections.deque(maxlen=1024)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(filename="invendor_app.log", level=logging.INFO)
    logger.info("Application start")
    ss =SwaggerSession(rbuf)
    ss.start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        cnt = 0
        while (True):
            data = s.recv(1024)
            timestamp = f"{datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec='milliseconds')}Z"
            latitude = struct.unpack('>f', data[0:4])[0]
            longitude = struct.unpack('>f', data[4:8])[0]
            #print(f"raw data {data.hex()} len {len(data)}")
            print(f"client socket recv ts: {timestamp} lat: {latitude} long: {longitude}")
            rbuf.append([timestamp, latitude, longitude])

    
