import logging
import sys


class StreamHandler(logging.StreamHandler):

    def __init__(self, level, formatter):
        logging.StreamHandler.__init__(self)

        self.setStream(sys.stdout)
        self.setLevel(level)
        if formatter is not None:
            self.setFormatter(formatter)
