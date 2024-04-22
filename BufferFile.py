
from threading import Lock
from threading import Timer
import collections
import shelve
import logging

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
        self.shelf = shelve.open(STORAGE_FNAME, writeback=True)
        self.shelf[STORAGE_TAG] = collections.deque(maxlen=144000) # 2 hours at 50ms
        self.data_buffer = self.shelf[STORAGE_TAG]
        Timer(1, self.backup_data).start()

    def __del__(self):
        self.shelf.close()

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
            raise LockAcquireError("Failed to acquire mutex lock")
        return entry
    
    def is_empty(self):
        if not bool(self.data_buffer):
            return True
        else:
            return False
    
    def backup_data(self):
        if self.is_empty():
            return
        lock_acquired = self.mutex_lock.acquire(timeout=0.1)
        if lock_acquired:
            self.shelf.sync()
            self.mutex_lock.release()





        
    