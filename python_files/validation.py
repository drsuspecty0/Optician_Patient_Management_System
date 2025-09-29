# validation.py
import datetime
from tkinter import messagebox

def validate_nonempty(text, field_name="Field"):
    """Checks that the input is not empty."""
    if not text.strip():
        messagebox.showerror("Input Error", f"{field_name} cannot be empty.")
        return False
    return True

def validate_future_date(date_text):
    """Checks that the date is in DD/MM/YYYY format and is in the future."""
    try:
        dt = datetime.datetime.strptime(date_text, "%d/%m/%Y")
        if dt <= datetime.datetime.now():
            messagebox.showerror("Date Error", "Date must be in the future.")
            return False
        return True
    except Exception:
        messagebox.showerror("Date Error", "Invalid date format. Use DD/MM/YYYY.")
        return False

def validate_past_date(date_text):
    """Checks that the date is in DD/MM/YYYY format and is in the past."""
    try:
        dt = datetime.datetime.strptime(date_text, "%d/%m/%Y")
        if dt >= datetime.datetime.now():
            messagebox.showerror("Date Error", "Date must be in the past.")
            return False
        return True
    except Exception:
        messagebox.showerror("Date Error", "Invalid date format. Use DD/MM/YYYY.")
        return False

def validate_phone(phone):
    """Checks that the phone number is exactly 10 digits."""
    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("Input Error", "Phone must be exactly 10 digits.")
        return False
    return True

def validate_age(age):
    """Checks that age is a number between 1 and 150."""
    if not age.isdigit() or not (1 <= int(age) <= 150):
        messagebox.showerror("Input Error", "Age must be a number between 1 and 150.")
        return False
    return True

def validate_email(email):
    """Checks that the email contains an '@' and a '.' after '@'."""
    if "@" not in email:
        messagebox.showerror("Input Error", "Invalid email address.")
        return False
    parts = email.split("@")
    if len(parts) < 2 or "." not in parts[1]:
        messagebox.showerror("Input Error", "Invalid email address.")
        return False
    return True

def validate_time(time_text):
    """Checks that time is in HH:MM format and between 09:00 and 19:00."""
    try:
        parts = time_text.split(":")
        if len(parts) != 2:
            raise ValueError
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 9 or hour >= 19:
            messagebox.showerror("Time Error", "Time must be between 09:00 and 19:00.")
            return False
        if minute < 0 or minute > 59:
            messagebox.showerror("Time Error", "Minutes must be between 0 and 59.")
            return False
        return True
    except Exception:
        messagebox.showerror("Time Error", "Invalid time format. Use HH:MM.")
        return False
