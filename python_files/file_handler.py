# file_handler.py
from constants import PATIENTS_FILE, APPOINTMENTS_FILE, PRESCRIPTIONS_FILE, ADMIN_FILE
from logger import log_error

def read_records(filename):
    """Reads all non-empty lines from a file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except Exception as e:
        log_error(f"Error reading {filename}: {e}")
        return []

def write_records(filename, records):
    """Overwrites the file with the given records."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for record in records:
                f.write(record.strip() + "\n")
    except Exception as e:
        log_error(f"Error writing to {filename}: {e}")

def append_record(filename, record):
    """Appends a single record to the given file."""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(record.strip() + "\n")
    except Exception as e:
        log_error(f"Error appending to {filename}: {e}")
