# Created by Lukas Ellemunt @ 01.06.2023
# Script to provide logging functionality

# system imports
from datetime import datetime
import os
import logging

# 3rd party imports
import colorlog


log_directory = "./logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File Handler
file_handler = logging.FileHandler(os.path.join(log_directory, 'log ' + datetime.now().strftime("%Y-%m-%d") + ".txt"))
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.WARNING) # uncomment if you only want warnings to be printed to console

# Create a ColorFormatter
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'reset',
        'INFO': 'reset',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red'
    },
    secondary_log_colors={},
    style='%'
)

console_handler.setFormatter(color_formatter)

logger.addHandler(console_handler)

