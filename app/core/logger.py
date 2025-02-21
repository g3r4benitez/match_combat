import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Principal Setting for logger
logger = logging.getLogger("challenge_notifications")
logger.setLevel(logging.DEBUG)

# Log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Manager to write logs in standar output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


os.makedirs("logs", exist_ok=True)


# Manager to write logs in file
file_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=3, delay=True)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
