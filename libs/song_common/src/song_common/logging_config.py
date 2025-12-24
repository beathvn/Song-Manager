from datetime import date
import logging
import os
import sys


def setup_logging():
    log_dir = "logs"
    current_day = date.today().strftime("%Y-%m-%d")
    log_filepath = os.path.join(log_dir, f"{current_day}.log")
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:  # guard against duplicate handlers
        return

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filepath, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
