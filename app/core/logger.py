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

log_dir = "/tmp/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")


# Manager to write logs in file
file_handler = RotatingFileHandler(filename=log_file, maxBytes=1000000, backupCount=3, delay=True)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
