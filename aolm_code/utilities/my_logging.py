
# Condition-less general debug output
import logging

# Loop progress output
from tqdm import tqdm

# Source: https://stackoverflow.com/questions/38543506/change-logging-print-function-to-tqdm-write-so-logging-doesnt-interfere-wit
# Initial source: https://github.com/tqdm/tqdm/issues/313 from user https://github.com/lrq3000
class TqdmLoggingHandler(logging.Handler):
    
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

# Logger initialization (debug with tqdm debug support)
logging.basicConfig(level=logging.DEBUG,
					handlers=[TqdmLoggingHandler(level=logging.DEBUG)])
# logging.basicConfig(level=logging.DEBUG)

debug_separator = "================================================================================"

def get_logger(p_name, p_level=logging.DEBUG, p_use_tqdm=True):

    # 1. Get logger instance with given name
    logger = logging.getLogger(p_name)

    # 2. Set up configuration for this logger instance

    # a. Level
    logger.setLevel(p_level)

    # b. Loop handling
    if p_use_tqdm:
        logger.addHandler(TqdmLoggingHandler(level=p_level))

    return logger
