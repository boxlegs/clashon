import logging
import os 


# Logger setup

logging_level_map = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}

LOGGING_LEVEL = logging_level_map[os.getenv('LOGGING_LEVEL', 'INFO')]
logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(level=LOGGING_LEVEL, format='%(name)s %(levelname)s: %(message)s')