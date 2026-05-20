import logging
import os
import sys

# Configure standard logging to stderr, so it doesn't pollute stdout (useful for piping JSON, etc.)
def setup_logging():
    level = logging.DEBUG if os.environ.get("KK_VERBOSE") == "1" else logging.WARNING
    
    # We want a very clean and simple output for CLI
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("kkcli")
    logger.setLevel(level)
    
    # Clear existing handlers to prevent duplicate messages
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)
    logger.propagate = False

setup_logging()

def get_logger():
    return logging.getLogger("kkcli")
