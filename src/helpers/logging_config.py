from datetime import date
import logging
import os
import sys


def setup_logging():
    """Configure logging settings for the entire application."""
    log_dir = "logs"
    current_day = date.today().strftime("%Y-%m-%d")
    log_filepath = os.path.join(log_dir, current_day + ".log")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_filepath), logging.StreamHandler(sys.stdout)],
    )
