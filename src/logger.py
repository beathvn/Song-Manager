# This file provides logging functionality


# system imports
from datetime import datetime
import logging


# create the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler(f'./logs/log {datetime.now().strftime("%Y-%m-%d")}.txt')
handler.setLevel(logging.DEBUG)

# create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(handler)
