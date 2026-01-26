import sys
from loguru import logger

def setup_logging():
    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    logger.add("logs/app.log", rotation="500 MB", level="DEBUG")

setup_logging()
