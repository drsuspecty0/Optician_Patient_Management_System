# logger.py
import datetime

def log_error(message):
    """Logs error messages with timestamps to a log file."""
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - ERROR: {message}\n")