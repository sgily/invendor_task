
from threading import Lock
import collections
import shelve
import logging
import time

STORAGE_FNAME = "coordinate_data"
STORAGE_TAG = 'store'
logger = logging.getLogger(__name__)

class LockAcquireError(Exception):
    pass

class Coordinates:
    def __init__(self, timestamp, latitude, longitude):
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    def as_payload(self):
        return {'createdDateTime': self.timestamp,
                'latitude': str(self.latitude),
                'longitude': str(self.longitude)}

class BufferFile:
    def __init__(self):
        self.mutex_lock = Lock()
        with shelve.open(STORAGE_FNAME, writeback=False) as shelf:
            logger.info(f"shelf keys {list(shelf.keys())}")
            if len(shelf.keys()) == 0:
                #self.shelf[STORAGE_TAG] = collections.deque(maxlen=144000) # 2 hours at 50ms
                logger.info("Creating new shelve file")
                self.data_buffer = collections.deque(maxlen=144000) # 2 hours at 50ms
            else:
                logger.info("Using existing shelf")
                self.data_buffer = shelf[STORAGE_TAG]

    def push_entry(self, timestamp, latitude, longitude):
        logger.info(f"push {timestamp} {latitude} {longitude}")
        lock_acquired = self.mutex_lock.acquire(timeout=0.1)
        if lock_acquired:
            self.data_buffer.append(Coordinates(timestamp, latitude, longitude))
            self.mutex_lock.release()
        else:
            raise LockAcquireError("Failed to acquire mutex lock")
    
    def pop_entry(self):
        if self.is_empty():
            return None
        lock_acquired = self.mutex_lock.acquire(timeout=0.1)
        if lock_acquired:
            entry = self.data_buffer.popleft()
            logger.info(f"popped {entry.as_payload()}")
            self.mutex_lock.release()
        else:
            entry = None
        return entry
    
    def is_empty(self):
        if not bool(self.data_buffer):
            return True
        else:
            return False
    
    def backup_data(self):
        if self.is_empty():
            logger.info("Nothing to back up")
        else:
            lock_acquired = self.mutex_lock.acquire(timeout=0.1)
            if lock_acquired:
                logger.info("Backing up data")
                ts = time.time_ns()
                with shelve.open(STORAGE_FNAME, writeback=False) as shelf:
                    shelf[STORAGE_TAG] = self.data_buffer
                    shelf.sync()
                logger.info(f"backup took {time.time_ns() - ts}")
                self.mutex_lock.release()





        
    