
import socket
import struct
from datetime import datetime,timezone
from SwaggerSession import SwaggerSession
import logging
from BufferFile import BufferFile
from BufferFile import LockAcquireError
from math import floor
import signal

HOST = "gpshost"  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on (non-privileged ports are > 1023)
logger = logging.getLogger(__name__)
BACKUP_PERIOD_S = 1

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    logger.info("Sigterm received")
    raise SystemExit

if __name__ == "__main__":
    logging.basicConfig(filename="invendor_app.log", level=logging.ERROR)
    logger.info("Application start")
    kill = GracefulKiller()
    rbuf = BufferFile()
    ss = SwaggerSession(rbuf)
    ss.start()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                current_ts = floor(datetime.now().timestamp())
                next_backup_ts = current_ts + BACKUP_PERIOD_S
                try:
                    s.connect((HOST, PORT))
                except (ConnectionRefusedError, socket.gaierror, OSError):
                    logger.error("Failed to connect to host, retrying")
                else:
                    cnt = 0
                    host_alive = True
                    while (host_alive):
                        try:
                            data = s.recv(1024)
                            if len(data) != 0:
                                timestamp = f"{datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec='milliseconds')}Z"
                                latitude = struct.unpack('>f', data[0:4])[0]
                                longitude = struct.unpack('>f', data[4:8])[0]
                                rbuf.push_entry(timestamp, latitude, longitude)
                            else:
                                logger.error("Host disconnected, waiting for connection")
                                host_alive = False
                        except LockAcquireError:
                            logger.error("Failed to acquire lock, packet lost")
                        else:
                            # Not a pretty solution for backing up data every n seconds
                            current_ts = floor(datetime.now().timestamp())
                            if (current_ts == next_backup_ts):
                                rbuf.backup_data()
                                next_backup_ts = floor(datetime.now().timestamp() + BACKUP_PERIOD_S)
    except (KeyboardInterrupt, SystemExit) as e:
        logger.error(f"Terminating program with {e=}")
    finally:
        ss.close()
        rbuf.backup_data()