import datetime as dt
import enum
import logging
import threading

from pymongo import MongoClient

from ted_sws import config
from ted_sws.event_manager.adapters.log.common import DEFAULT_LOGGER_LEVEL

BUFFER_PERIODICAL_FLUSH_TIMING = config.LOGGER_MONGO_HANDLER_BUFFER_PERIODICAL_FLUSH_TIMING
DEFAULT_BUFFER_SIZE = 0
DEFAULT_MONGO_CLIENT = MongoClient(config.MONGO_DB_AUTH_URL)

LOGS_DB = config.MONGO_DB_LOGS_DATABASE_NAME
LOGS_COLLECTION = config.MONGO_DB_LOGS_COLLECTION


class KPILogCollection(enum.Enum):
    NOTICE = "notice"
    MAPPING_SUITE = "mapping_suite"
    PIPELINE = "pipeline"
    QUALITY = "quality"


"""
Example format of generated bson document:
{
    'thread': -1216977216,
    'threadName': 'MainThread',
    'level': 'ERROR',
    'timestamp': datetime.datetime(2016, 8, 16, 15, 20, 24, 794341),
    'message': 'test message',
    'module': 'test_module',
    'fileName': 'test_handlers',
    'lineNumber': 38,
    'method': 'test_emit_exception',
    'loggerName':  'testLogger',
    'exception': {
        'stackTrace': 'Traceback (most recent call last):
                       File "test_handlers.py", line 36, in test_emit_exception
                       raise Exception(\'exc1\')
                       Exception: exc1',
        'message': 'exc1',
        'code': 0
    }
}
"""
_connection = None


class MongoFormatter(logging.Formatter):
    DEFAULT_PROPERTIES = logging.LogRecord(
        '', DEFAULT_LOGGER_LEVEL, '', 0, '', None, None, '').__dict__.keys()

    def format(self, record):
        """Formats LogRecord into python dictionary."""
        # Standard document
        document = {
            'timestamp': dt.datetime.utcnow(),
            'level': record.levelname,
            'thread': record.thread,
            'threadName': record.threadName,
            'message': record.getMessage(),
            'loggerName': record.name,
            # 'fileName': record.pathname,
            'module': record.module,
            'method': record.funcName,
            'lineNumber': record.lineno
        }
        # Standard document decorated with exception info
        if record.exc_info is not None:
            document.update({
                'exception': {
                    'message': str(record.exc_info[1]),
                    'code': 0,
                    'stackTrace': self.formatException(record.exc_info)
                }
            })
        # Standard document decorated with extra contextual information
        if len(self.DEFAULT_PROPERTIES) != len(record.__dict__):
            contextual_extra = set(record.__dict__).difference(
                set(self.DEFAULT_PROPERTIES))
            if contextual_extra:
                for key in contextual_extra:
                    document[key] = record.__dict__[key]
        return document


class MongoHandler(logging.Handler):

    def __init__(self,
                 level=DEFAULT_LOGGER_LEVEL,
                 mongodb_client: MongoClient = DEFAULT_MONGO_CLIENT,
                 database_name=LOGS_DB,
                 collection=LOGS_COLLECTION,
                 fail_silently=False,
                 formatter=None,
                 reuse=True
                 ):
        """
        Setting up mongo handler, initializing mongo database connection via
        pymongo.

        If reuse is set to false every handler will have it's own MongoClient.
        This could hammer down your MongoDB instance, but you can still use
        this option.

        The default is True. As such a program with multiple handlers
        that log to mongodb will have those handlers share a single connection
        to MongoDB.
        """
        logging.Handler.__init__(self, level)
        self.connection = mongodb_client
        self.database_name = database_name
        self.collection_name = collection
        self.update_collection_name()
        self.fail_silently = fail_silently
        self.db = None
        self.collection = None
        self.authenticated = False
        self.formatter = formatter or MongoFormatter()
        self.reuse = reuse
        self._connect()

    def update_collection_name(self):
        if self.collection_name:
            self.collection_name = dt.date.today().strftime("%Y_") + self.collection_name

    def _connect(self):
        """Connecting to mongo database."""
        global _connection
        if self.reuse and _connection:
            self.connection = _connection
        else:
            _connection = self.connection

        self.db = self.connection[self.database_name]

        if self.collection_name:
            self.collection = self.db[self.collection_name]

    def close(self):
        """
        If authenticated, logging out and closing mongo database connection.
        """
        if self.authenticated:
            self.db.logout()
        if self.connection is not None:
            self.connection.close()

    def emit(self, record):
        """Inserting new logging record to mongo database."""
        if self.collection is not None:
            try:
                self.collection.insert_one(self.format(record))
            except Exception:
                if not self.fail_silently:
                    self.handleError(record)

    def __exit__(self, type, value, traceback):
        self.close()


class BufferedMongoHandler(MongoHandler):

    def __init__(self,
                 level=DEFAULT_LOGGER_LEVEL,
                 mongodb_client: MongoClient = DEFAULT_MONGO_CLIENT,
                 database_name=LOGS_DB,
                 collection=LOGS_COLLECTION,
                 fail_silently=False,
                 formatter=None,
                 reuse=True,
                 buffer_size=DEFAULT_BUFFER_SIZE,
                 buffer_periodical_flush_timing=BUFFER_PERIODICAL_FLUSH_TIMING,
                 buffer_early_flush_level=logging.CRITICAL
                 ):
        """
        Setting up buffered mongo handler, initializing mongo database connection via
        pymongo.

        This subclass aims to provide buffering mechanism to avoid hammering the database server and
        write-locking the database too often (even if mongo is performant in that matter).

        If buffer_periodical_flush_timer is set to None or 0, no periodical flush of the buffer will be done.
        It means that buffered messages might be stuck here for a while until the buffer full or
        a critical message is sent (both causing flush).

        If buffer_periodical_flush_timer is set to numeric value, a thread with timer will be launched
        to call the buffer flush periodically.
        """

        MongoHandler.__init__(self,
                              level=level,
                              mongodb_client=mongodb_client,
                              database_name=database_name,
                              collection=collection,
                              fail_silently=fail_silently,
                              formatter=formatter,
                              reuse=reuse
                              )
        self.buffer = []
        self.buffer_size = buffer_size
        self.buffer_periodical_flush_timing = buffer_periodical_flush_timing
        self.buffer_early_flush_level = buffer_early_flush_level
        self.last_record = None  # kept for handling the error on flush
        self.buffer_timer_thread = None

        self.buffer_lock = threading.RLock()

        self._timer_stopper = None

        # setup periodical flush
        if self.buffer_periodical_flush_timing:

            # clean exit event
            import atexit
            atexit.register(self.destroy)

            # call at interval function
            def call_repeatedly(interval, func, *args):
                stopped = threading.Event()

                # actual thread function
                def loop():
                    while not stopped.wait(interval):  # the first call is in `interval` secs
                        func(*args)

                timer_thread = threading.Thread(target=loop)
                timer_thread.daemon = True
                timer_thread.start()
                return stopped.set, timer_thread

            # launch thread
            self._timer_stopper, self.buffer_timer_thread = call_repeatedly(self.buffer_periodical_flush_timing,
                                                                            self.flush_to_mongo)

    def emit(self, record):
        """Inserting new logging record to buffer and flush if necessary."""
        with self.buffer_lock:
            self.last_record = record
            self.buffer.append(self.format(record))

        if len(self.buffer) >= self.buffer_size or record.levelno >= self.buffer_early_flush_level:
            self.flush_to_mongo()

    def flush_to_mongo(self):
        """Flush all records to mongo database."""
        if self.collection is not None and len(self.buffer) > 0:
            with self.buffer_lock:
                try:
                    self.collection.insert_many(self.buffer)
                    self.empty_buffer()
                except Exception:
                    if not self.fail_silently:
                        self.handleError(self.last_record)  # handling the error on flush

    def empty_buffer(self):
        """Empty the buffer list."""
        del self.buffer
        self.buffer = []

    def destroy(self):
        """Clean quit logging. Flush buffer. Stop the periodical thread if needed."""
        if self._timer_stopper:
            self._timer_stopper()
        self.flush_to_mongo()
        self.close()
