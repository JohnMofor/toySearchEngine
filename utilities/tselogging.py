from logging import *  # @UnusedWildImport
import logging.config  # To make this module more portable.
import getpass
from toySearchEngine.settings import LOGGING


class TseLogRecord(logging.LogRecord):

    """ Adds a userName attribute to the built-in logRecord"""

    def __init__(self, *args, **kwargs):
        logging.LogRecord.__init__(self, *args, **kwargs)
        self.userName = getpass.getuser()


class TseLogger(logging.getLoggerClass()):

    """ Used to inject TseLogRecord into logging """

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        rec = TseLogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rec.__dict__):
                    raise KeyError(
                        "Attempt to overwrite %r in TseLogRecord" % key)
                rec.__dict__[key] = extra[key]
        return rec


def setupTseLogger():
    print "Initializing TseLogger"
    logging.setLoggerClass(TseLogger)
    logging.config.dictConfig(LOGGING)
    print "TseLogger initialization complete"

# Perform the TseLogger Initialization
setupTseLogger()
