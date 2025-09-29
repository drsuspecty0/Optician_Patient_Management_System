# ui.py
import tkinter as tk
from tkinter import messagebox
import datetime
import hashlib

from constants import PATIENTS_FILE, APPOINTMENTS_FILE, PRESCRIPTIONS_FILE, ADMIN_FILE
from file_handler import read_records, write_records, append_record
from validation import (validate_nonempty, validate_future_date, validate_past_date,
                        validate_phone, validate_age, validate_email, validate_time)

# ---------- Helper Functions ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Passwords
password1 = "password123"
password2 = "mrivera123"

# Generate hashes
hash1 = hash_password(password1)
hash2 = hash_password(password2)

print(f"Hash for 'password123': {hash1}")
print(f"Hash for 'mrivera123': {hash2}")

def get_patient_by_name(full_name):
    """Return patient ID by matching any part (first, last, or full) of the name."""
    full_name = full_name.strip().lower()
    records = read_records(PATIENTS_FILE)
    matches = []
    for rec in records:
        parts = rec.split(",")
        if len(parts) < 3:
            continue
        first = parts[1].strip().lower()
        last = parts[2].strip().lower()
        combined = f"{first} {last}"
        if full_name in first or full_name in last or full_name in combined:
            matches.append(parts[0].strip())
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        messagebox.showerror("Ambiguity", "Multiple patients match the name. Please specify by ID.")
        return None
    else:
        return None

def get_patient_full_name(pid):
    """Returns the full name for the given patient ID."""
    records = read_records(PATIENTS_FILE)
    for rec in records:
        parts = rec.split(",")
        if parts[0].strip() == pid:
            return f"{parts[1].strip()} {parts[2].strip()}"
    return "Unknown"

def get_patient_id(identifier):
    """If identifier is numeric, returns it; otherwise, uses name lookup."""
    identifier = identifier.strip()
    if identifier.isdigit():
        return identifier
    else:
        return get_patient_by_name(identifier)

# ---------- ADMIN LOGIN ----------
def load_admins():
    """Reads admins from ADMIN_FILE. Format: AdminID,Username,PasswordHash."""
    admins = {}
    records = read_records(ADMIN_FILE)
    for rec in records:
        parts = rec.split(",")
        if len(parts) >= 3:
            username = parts[1].strip()
            password_hash = parts[2].strip()
            admins[username] = password_hash
    return admins

def login():
    """Handles the admin login process."""
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    admins = load_admins()
    password_hash = hash_password(password)
    
    # Log the entered username and password hash
    print(f"Entered Username: {username}")
    print(f"Entered Password Hash: {password_hash}")
    
    if username in admins:
        print(f"Stored Password Hash: {admins[username]}")
        if admins[username] == password_hash:
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            login_root.destroy()
            open_main_ui()
        else:
            messagebox.showerror("Login Failed", "Invalid password.")
    else:
        messagebox.showerror("Login Failed", "Invalid username.")

# ---------- PATIENT MANAGEMENT ----------
def generate_patient_id():
    """Generates a new unique patient ID."""
    records = read_records(PATIENTS_FILE)
    max_id = 0
    for rec in records:
        try:
            pid = int(rec.split(",")[0].strip())
            if pid > max_id:
                max_id = pid
        except:
            continue
    return str(max_id + 1)

def add_patient():
    """Opens a window to add a new patient."""
    win = tk.Toplevel(main_ui)
    win.title("Add Patient")
    tk.Label(win, text="First Name:").pack()
    first_entry = tk.Entry(win)
    first_entry.pack()
    tk.Label(win, text="Last Name:").pack()
    last_entry = tk.Entry(win)
    last_entry.pack()
    tk.Label(win, text="Date of Birth (DD/MM/YYYY):").pack()
    dob_entry = tk.Entry(win)
    dob_entry.pack()
    tk.Label(win, text="Phone (10 digits):").pack()
    phone_entry = tk.Entry(win)
    phone_entry.pack()
    tk.Label(win, text="Email:").pack()
    email_entry = tk.Entry(win)
    email_entry.pack()
    tk.Label(win, text="Address:").pack()
    address_entry = tk.Entry(win)
    address_entry.pack()
    
    def save():
        """Saves the new patient record."""
        first = first_entry.get().strip()
        last = last_entry.get().strip()
        dob = dob_entry.get().strip()
        phone = phone_entry.get().strip()
        email = email_entry.get().strip()
        address = address_entry.get().strip()
        if not (validate_nonempty(first, "First Name") and
                validate_nonempty(last, "Last Name") and
                validate_nonempty(dob, "Date of Birth") and
                validate_nonempty(phone, "Phone") and
                validate_nonempty(email, "Email") and
                validate_nonempty(address, "Address")):
            return
        if not validate_past_date(dob):
            return
        if not (validate_phone(phone) and validate_email(email)):
            return
        pid = generate_patient_id()
        record = f"{pid},{first},{last},{dob},{phone},{email},{address}"
        append_record(PATIENTS_FILE, record)
        messagebox.showinfo("Success", f"Patient added with ID {pid}.")
        win.destroy()
        # Automatically open appointment booking with the new patient's full name.
        book_appointment(f"{first} {last}")
    tk.Button(win, text="Save", command=save).pack()

def search_patient():
    """Opens a window to search for a patient."""
    win = tk.Toplevel(main_ui)
    win.title("Search Patient")
    tk.Label(win, text="Enter Full Name (First Last):").pack()
    query_entry = tk.Entry(win)
    query_entry.pack()
    def search():
        """Searches for a patient by full name."""
        query = query_entry.get().strip().lower()
        records = read_records(PATIENTS_FILE)
        results = []
        for rec in records:
            parts = rec.split(",")
            if len(parts) >= 3:
                full_name = f"{parts[1].strip()} {parts[2].strip()}".lower()
                if query in full_name:
                    results.append(rec)
        if results:
            messagebox.showinfo("Results", "\n".join(results))
        else:
            messagebox.showinfo("Results", "No matching patient found.")
    tk.Button(win, text="Search", command=search).pack()

def edit_patient():
    """Opens a window to edit an existing patient record."""
    win = tk.Toplevel(main_ui)
    win.title("Edit Patient")
    tk.Label(win, text="Enter Patient ID or Full Name:").pack()
    id_entry = tk.Entry(win)
    id_entry.pack()
    first_var = tk.StringVar()
    last_var = tk.StringVar()
    dob_var = tk.StringVar()
    phone_var = tk.StringVar()
    email_var = tk.StringVar()
    address_var = tk.StringVar()
    def load():
        """Loads the patient record for editing."""
        identifier = id_entry.get().strip()
        pid = get_patient_id(identifier)
        if not pid:
            messagebox.showerror("Error", "Patient not found.")
            return
        records = read_records(PATIENTS_FILE)
        for rec in records:
            parts = rec.split(",")
            if parts[0].strip() == pid:
                first_var.set(parts[1].strip())
                last_var.set(parts[2].strip())
                dob_var.set(parts[3].strip())
                phone_var.set(parts[4].strip())
                email_var.set(parts[5].strip())
                address_var.set(parts[6].strip())
                return
        messagebox.showerror("Error", "Patient not found.")
    tk.Button(win, text="Load", command=load).pack()
    tk.Label(win, text="New First Name:").pack()
    tk.Entry(win, textvariable=first_var).pack()
    tk.Label(win, text="New Last Name:").pack()
    tk.Entry(win, textvariable=last_var).pack()
    tk.Label(win, text="New Date of Birth (DD/MM/YYYY):").pack()
    tk.Entry(win, textvariable=dob_var).pack()
    tk.Label(win, text="New Phone:").pack()
    tk.Entry(win, textvariable=phone_var).pack()
    tk.Label(win, text="New Email:").pack()
    tk.Entry(win, textvariable=email_var).pack()
    tk.Label(win, text="New Address:").pack()
    tk.Entry(win, textvariable=address_var).pack()
    def update():
        """Updates the patient record."""
        identifier = id_entry.get().strip()
        pid = get_patient_id(identifier)
        if not pid:
            messagebox.showerror("Error", "Patient not found.")
            return
        first = first_var.get().strip()
        last = last_var.get().strip()
        dob = dob_var.get().strip()
        phone = phone_var.get().strip()
        email = email_var.get().strip()
        address = address_var.get().strip()
        if not (validate_nonempty(first, "First Name") and
                validate_nonempty(last, "Last Name") and
                validate_nonempty(dob, "Date of Birth") and
                validate_nonempty(phone, "Phone") and
                validate_nonempty(email, "Email") and
                validate_nonempty(address, "Address")):
            return
        if not validate_past_date(dob):
            return
        if not (validate_phone(phone) and validate_email(email)):
            return
        records = read_records(PATIENTS_FILE)
        updated_records = []
        found = False
        for rec in records:
            parts = rec.split(",")
            if parts[0].strip() == pid:
                updated_records.append(f"{pid},{first},{last},{dob},{phone},{email},{address}")
                found = True
            else:
                updated_records.append(rec)
        if found:
            write_records(PATIENTS_FILE, updated_records)
            messagebox.showinfo("Success", "Patient record updated.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Patient not found.")
    tk.Button(win, text="Update", command=update).pack()

def delete_patient():
    """Opens a window to delete a patient record."""
    win = tk.Toplevel(main_ui)
    win.title("Delete Patient")
    tk.Label(win, text="Enter Patient ID or Full Name:").pack()
    id_entry = tk.Entry(win)
    id_entry.pack()
    def delete():
        """Deletes the patient record."""
        identifier = id_entry.get().strip()
        pid = get_patient_id(identifier)
        if not pid:
            messagebox.showerror("Error", "Patient not found.")
            return
        records = read_records(PATIENTS_FILE)
        updated = [rec for rec in records if rec.split(",")[0].strip() != pid]
        if len(records) == len(updated):
            messagebox.showerror("Error", "Patient not found.")
        else:
            write_records(PATIENTS_FILE, updated)
            # Cascade deletion in appointments and prescriptions.
            apps = read_records(APPOINTMENTS_FILE)
            apps = [app for app in apps if app.split(",")[1].strip() != pid]
            write_records(APPOINTMENTS_FILE, apps)
            prescs = read_records(PRESCRIPTIONS_FILE)
            prescs = [p for p in prescs if p.split(",")[1].strip() != pid]
            write_records(PRESCRIPTIONS_FILE, prescs)
            messagebox.showinfo("Success", f"Patient with ID {pid} and related records deleted.")
            win.destroy()
    tk.Button(win, text="Delete", command=delete).pack()

def view_patients():
    """Opens a window to view all patient records."""
    win = tk.Toplevel(main_ui)
    win.title("View Patients")
    text_area = tk.Text(win, width=80, height=20)
    text_area.pack()
    def refresh():
        """Refreshes the list of patient records."""
        text_area.delete("1.0", tk.END)
        records = read_records(PATIENTS_FILE)
        if records:
            text_area.insert(tk.END, "\n".join(records))
        else:
            text_area.insert(tk.END, "No patient records.")
    tk.Button(win, text="Refresh", command=refresh).pack()
    refresh()

# ---------- APPOINTMENT MANAGEMENT ----------
def generate_appointment_id():
    """Generates a new unique appointment ID."""
    records = read_records(APPOINTMENTS_FILE)
    max_id = 0
    for rec in records:
        try:
            aid = int(rec.split(",")[0].strip())
            if aid > max_id:
                max_id = aid
        except:
            continue
    return str(max_id + 1)

def book_appointment(default_name=""):
    """Opens a window to book a new appointment."""
    win = tk.Toplevel(main_ui)
    win.title("Book Appointment")
    tk.Label(win, text="Patient Full Name (First Last):").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()
    if default_name:
        name_entry.insert(0, default_name)
    tk.Label(win, text="Appointment Date (DD/MM/YYYY):").pack()
    date_entry = tk.Entry(win)
    date_entry.pack()
    tk.Label(win, text="Appointment Time (HH:MM, 09:00-19:00):").pack()
    time_entry = tk.Entry(win)
    time_entry.pack()
    tk.Label(win, text="Reason:").pack()
    reason_entry = tk.Entry(win)
    reason_entry.pack()
    def book():
        """Books the appointment."""
        full_name = name_entry.get().strip()
        date = date_entry.get().strip()
        time_str = time_entry.get().strip()
        reason = reason_entry.get().strip()
        if not (validate_nonempty(full_name, "Patient Full Name") and
                validate_nonempty(date, "Date") and
                validate_nonempty(time_str, "Time") and
                validate_nonempty(reason, "Reason")):
            return
        if not (validate_future_date(date) and validate_time(time_str)):
            return
        # Check for appointment conflict: same date & time already booked.
        existing = [rec for rec in read_records(APPOINTMENTS_FILE)
                    if rec.split(",")[3].strip() == date and
                       rec.split(",")[4].strip() == time_str and
                       rec.split(",")[5].strip().lower() == "booked"]
        if existing:
            messagebox.showerror("Conflict", "This appointment slot is already booked.")
            return
        pid = get_patient_by_name(full_name)
        if not pid:
            messagebox.showerror("Error", "Patient not found. Please add the patient first.")
            return
        aid = generate_appointment_id()
        record = f"{aid},{pid},{full_name},{date},{time_str},Booked,{reason}"
        append_record(APPOINTMENTS_FILE, record)
        messagebox.showinfo("Success", f"Appointment booked with ID {aid}.")
        win.destroy()
    tk.Button(win, text="Book", command=book).pack()

def delete_appointment():
    """Opens a window to delete an appointment."""
    win = tk.Toplevel(main_ui)
    win.title("Delete Appointment")
    tk.Label(win, text="Enter Patient Full Name (First Last):").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()
    tk.Label(win, text="Enter Appointment Date (DD/MM/YYYY):").pack()
    date_entry = tk.Entry(win)
    date_entry.pack()
    tk.Label(win, text="Enter Appointment Time (HH:MM):").pack()
    time_entry = tk.Entry(win)
    time_entry.pack()
    def delete():
        """Deletes the appointment."""
        full_name = name_entry.get().strip().lower()
        date = date_entry.get().strip()
        time_str = time_entry.get().strip()
        pid = get_patient_by_name(full_name)
        if not pid:
            messagebox.showerror("Error", "Patient not found.")
            return
        records = read_records(APPOINTMENTS_FILE)
        updated = [rec for rec in records if not (rec.split(",")[1].strip() == pid and 
                                                   rec.split(",")[3].strip() == date and 
                                                   rec.split(",")[4].strip() == time_str)]
        if len(records) == len(updated):
            messagebox.showerror("Error", "Appointment not found.")
        else:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this appointment?"):
                write_records(APPOINTMENTS_FILE, updated)
                messagebox.showinfo("Success", "Appointment deleted.")
                win.destroy()
    tk.Button(win, text="Delete", command=delete).pack()

def extend_appointment():
    """Opens a window to extend an appointment."""
    win = tk.Toplevel(main_ui)
    win.title("Extend Appointment")
    tk.Label(win, text="Enter Appointment ID:").pack()
    aid_entry = tk.Entry(win)
    aid_entry.pack()
    tk.Label(win, text="Enter New Date (DD/MM/YYYY):").pack()
    date_entry = tk.Entry(win)
    date_entry.pack()
    tk.Label(win, text="Enter New Time (HH:MM):").pack()
    time_entry = tk.Entry(win)
    time_entry.pack()
    def extend():
        """Extends the appointment."""
        aid = aid_entry.get().strip()
        new_date = date_entry.get().strip()
        new_time = time_entry.get().strip()
        if not (validate_nonempty(new_date, "New Date") and validate_nonempty(new_time, "New Time")):
            return
        if not (validate_future_date(new_date) and validate_time(new_time)):
            return
        records = read_records(APPOINTMENTS_FILE)
        updated = []
        found = False
        for rec in records:
            parts = rec.split(",")
            if parts[0].strip() == aid:
                # Check if new slot is available:
                conflict = [r for r in records if r.split(",")[3].strip() == new_date and 
                            r.split(",")[4].strip() == new_time and r.split(",")[5].strip().lower() == "booked"]
                if conflict:
                    messagebox.showerror("Conflict", "The new appointment slot is already booked.")
                    return
                updated.append(f"{aid},{parts[1].strip()},{parts[2].strip()},{new_date},{new_time},Booked,{parts[6].strip()}")
                found = True
            else:
                updated.append(rec)
        if found:
            write_records(APPOINTMENTS_FILE, updated)
            messagebox.showinfo("Success", "Appointment extended.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Appointment not found.")
    tk.Button(win, text="Extend", command=extend).pack()

def view_appointments():
    win = tk.Toplevel(main_ui)
    win.title("View Appointments")
    text_area = tk.Text(win, width=80, height=20)
    text_area.pack()
    def refresh():
        text_area.delete("1.0", tk.END)
        records = read_records(APPOINTMENTS_FILE)
        if records:
            text_area.insert(tk.END, "\n".join(records))
        else:
            text_area.insert(tk.END, "No appointments found.")
    tk.Button(win, text="Refresh", command=refresh).pack()
    refresh()

# ---------- PRESCRIPTION MANAGEMENT ----------
def generate_prescription_id():
    records = read_records(PRESCRIPTIONS_FILE)
    max_id = 0
    for rec in records:
        try:
            pid = int(rec.split(",")[0].strip())
            if pid > max_id:
                max_id = pid
        except:
            continue
    return str(max_id + 1)

def add_prescription():
    win = tk.Toplevel(main_ui)
    win.title("Add Prescription")
    tk.Label(win, text="Patient Full Name (First Last):").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()
    tk.Label(win, text="Prescription Details:").pack()
    details_entry = tk.Entry(win)
    details_entry.pack()
    tk.Label(win, text="Prescription Date (DD/MM/YYYY):").pack()
    date_entry = tk.Entry(win)
    date_entry.pack()
    def add():
        full_name = name_entry.get().strip()
        details = details_entry.get().strip()
        presc_date = date_entry.get().strip()
        if not (validate_nonempty(full_name, "Patient Full Name") and
                validate_nonempty(details, "Details") and
                validate_nonempty(presc_date, "Prescription Date")):
            return
        try:
            dt = datetime.datetime.strptime(presc_date, "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Date Error", "Invalid date format. Use DD/MM/YYYY.")
            return
        expiry_dt = dt + datetime.timedelta(days=365)
        expiry = expiry_dt.strftime("%d/%m/%Y")
        pid = get_patient_by_name(full_name)
        if not pid:
            messagebox.showerror("Error", "Patient not found. Please add the patient first.")
            return
        presc_id = generate_prescription_id()
        record = f"{presc_id},{pid},{full_name},{details},{presc_date},{expiry}"
        append_record(PRESCRIPTIONS_FILE, record)
        messagebox.showinfo("Success", f"Prescription added with ID {presc_id}.")
        win.destroy()
    tk.Button(win, text="Add", command=add).pack()

def edit_prescription():
    win = tk.Toplevel(main_ui)
    win.title("Edit Prescription")
    tk.Label(win, text="Enter Prescription ID or Patient Full Name:").pack()
    id_entry = tk.Entry(win)
    id_entry.pack()
    new_var = tk.StringVar()
    def load():
        identifier = id_entry.get().strip()
        records = read_records(PRESCRIPTIONS_FILE)
        found = False
        for rec in records:
            parts = rec.split(",")
            if parts[0].strip() == identifier:
                new_var.set(parts[3].strip())
                found = True
                break
        if not found:
            pid = get_patient_by_name(identifier)
            if pid:
                for rec in records:
                    parts = rec.split(",")
                    if parts[1].strip() == pid:
                        new_var.set(parts[3].strip())
                        found = True
                        break
        if not found:
            messagebox.showerror("Error", "Prescription not found.")
    tk.Button(win, text="Load", command=load).pack()
    tk.Label(win, text="New Prescription Details:").pack()
    tk.Entry(win, textvariable=new_var).pack()
    def update():
        identifier = id_entry.get().strip()
        new_details = new_var.get().strip()
        if not validate_nonempty(new_details, "Prescription Details"):
            return
        records = read_records(PRESCRIPTIONS_FILE)
        updated = []
        found = False
        for rec in records:
            parts = rec.split(",")
            if parts[0].strip() == identifier or (get_patient_by_name(identifier) and parts[1].strip() == get_patient_by_name(identifier)):
                updated.append(f"{parts[0].strip()},{parts[1].strip()},{parts[2].strip()},{new_details},{parts[4].strip()},{parts[5].strip()}")
                found = True
            else:
                updated.append(rec)
        if found:
            write_records(PRESCRIPTIONS_FILE, updated)
            messagebox.showinfo("Success", "Prescription updated.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Prescription not found.")
    tk.Button(win, text="Update", command=update).pack()

def delete_prescription():
    win = tk.Toplevel(main_ui)
    win.title("Delete Prescription")
    tk.Label(win, text="Enter Patient Full Name (First Last):").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()
    def delete():
        full_name = name_entry.get().strip().lower()
        pid = get_patient_by_name(full_name)
        if not pid:
            messagebox.showerror("Error", "Patient not found.")
            return
        records = read_records(PRESCRIPTIONS_FILE)
        updated = [rec for rec in records if rec.split(",")[1].strip() != pid]
        if len(records) == len(updated):
            messagebox.showerror("Error", "Prescription not found.")
        else:
            if messagebox.askyesno("Confirm", "Delete prescription for this patient?"):
                write_records(PRESCRIPTIONS_FILE, updated)
                messagebox.showinfo("Success", "Prescription deleted.")
                win.destroy()
    tk.Button(win, text="Delete", command=delete).pack()

def view_prescriptions():
    win = tk.Toplevel(main_ui)
    win.title("View Prescriptions")
    text_area = tk.Text(win, width=80, height=20)
    text_area.pack()
    def refresh():
        text_area.delete("1.0", tk.END)
        records = read_records(PRESCRIPTIONS_FILE)
        if records:
            text_area.insert(tk.END, "\n".join(records))
        else:
            text_area.insert(tk.END, "No prescriptions found.")
    tk.Button(win, text="Refresh", command=refresh).pack()
    refresh()

# ---------- INACTIVE PATIENTS CLEANUP (by Prescription Date) ----------
def view_inactive_patients():
    """
    Displays patients for whom the most recent prescription date is over 4 years old
    (or they have no prescription) with options to delete them.
    """
    win = tk.Toplevel(main_ui)
    win.title("Inactive Patients (4+ Years)")
    text_area = tk.Text(win, width=80, height=20)
    text_area.pack()
    
    now = datetime.datetime.now()
    threshold = now - datetime.timedelta(days=4*365)
    patients = read_records(PATIENTS_FILE)
    inactive = []
    for rec in patients:
        parts = rec.split(",")
        pid = parts[0].strip()
        prescs = [p for p in read_records(PRESCRIPTIONS_FILE) if p.split(",")[1].strip() == pid]
        latest_date = None
        for presc in prescs:
            try:
                presc_date = presc.split(",")[4].strip()
                dt = datetime.datetime.strptime(presc_date, "%d/%m/%Y")
                if (latest_date is None) or (dt > latest_date):
                    latest_date = dt
            except:
                continue
        # If no prescription exists or latest is older than threshold, mark inactive.
        if latest_date is None or latest_date < threshold:
            inactive.append(rec)
    if inactive:
        text_area.insert(tk.END, "\n".join(inactive))
    else:
        text_area.insert(tk.END, "No inactive patients found.")
    
    def delete_inactive():
        if messagebox.askyesno("Confirm", "Delete all inactive patient records? This will also delete related appointments and prescriptions."):

            inactive_ids = [rec.split(",")[0].strip() for rec in inactive]
            remaining = [rec for rec in patients if rec.split(",")[0].strip() not in inactive_ids]
            write_records(PATIENTS_FILE, remaining)
            apps = [app for app in read_records(APPOINTMENTS_FILE) if app.split(",")[1].strip() not in inactive_ids]
            write_records(APPOINTMENTS_FILE, apps)
            prescs = [p for p in read_records(PRESCRIPTIONS_FILE) if p.split(",")[1].strip() not in inactive_ids]
            write_records(PRESCRIPTIONS_FILE, prescs)
            messagebox.showinfo("Success", "Inactive patient records and related data deleted.")
            win.destroy()
    tk.Button(win, text="Delete All Inactive", command=delete_inactive, bg="#8B0000", fg="white").pack()

def cleanup_records():
    view_inactive_patients()

# ---------- MAIN UI WINDOW ----------
def open_main_ui():
    global main_ui
    main_ui = tk.Tk()
    main_ui.title("Optician Patient Management System")
    main_ui.geometry("900x700")
    main_ui.configure(bg="#f4f4f4")
    
    patient_frame = tk.Frame(main_ui, bg="white", padx=10, pady=10)
    patient_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
    appointment_frame = tk.Frame(main_ui, bg="white", padx=10, pady=10)
    appointment_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
    prescription_frame = tk.Frame(main_ui, bg="white", padx=10, pady=10)
    prescription_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
    
    tk.Label(patient_frame, text="Patient Management", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, pady=5)
    tk.Button(patient_frame, text="Add Patient", command=add_patient, font=("Arial", 10), bg="#28A745", fg="white", width=18).grid(row=1, column=0, pady=2)
    tk.Button(patient_frame, text="Search Patient", command=search_patient, font=("Arial", 10), bg="#007BFF", fg="white", width=18).grid(row=2, column=0, pady=2)
    tk.Button(patient_frame, text="Edit Patient", command=edit_patient, font=("Arial", 10), bg="#FFC107", width=18).grid(row=3, column=0, pady=2)
    tk.Button(patient_frame, text="Delete Patient", command=delete_patient, font=("Arial", 10), bg="#DC3545", fg="white", width=18).grid(row=4, column=0, pady=2)
    tk.Button(patient_frame, text="View Patients", command=view_patients, font=("Arial", 10), bg="#6C757D", fg="white", width=18).grid(row=5, column=0, pady=2)
    
    tk.Label(appointment_frame, text="Appointment Management", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, pady=5)
    tk.Button(appointment_frame, text="Book Appointment", command=lambda: book_appointment(), font=("Arial", 10), bg="#17A2B8", fg="white", width=18).grid(row=1, column=0, pady=2)
    tk.Button(appointment_frame, text="Delete Appointment", command=delete_appointment, font=("Arial", 10), bg="#DC3545", fg="white", width=18).grid(row=2, column=0, pady=2)
    tk.Button(appointment_frame, text="Extend Appointment", command=extend_appointment, font=("Arial", 10), bg="#FFC107", width=18).grid(row=3, column=0, pady=2)
    tk.Button(appointment_frame, text="View Appointments", command=view_appointments, font=("Arial", 10), bg="#6C757D", fg="white", width=18).grid(row=4, column=0, pady=2)
    
    tk.Label(prescription_frame, text="Prescription Management", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, pady=5)
    tk.Button(prescription_frame, text="Add Prescription", command=add_prescription, font=("Arial", 10), bg="#6C757D", fg="white", width=18).grid(row=1, column=0, pady=2)
    tk.Button(prescription_frame, text="Edit Prescription", command=edit_prescription, font=("Arial", 10), bg="#FFC107", width=18).grid(row=2, column=0, pady=2)
    tk.Button(prescription_frame, text="Delete Prescription", command=delete_prescription, font=("Arial", 10), bg="#DC3545", fg="white", width=18).grid(row=3, column=0, pady=2)
    tk.Button(prescription_frame, text="View Prescriptions", command=view_prescriptions, font=("Arial", 10), bg="#007BFF", fg="white", width=18).grid(row=4, column=0, pady=2)
    
    tk.Button(main_ui, text="View & Cleanup Inactive Patients", command=view_inactive_patients, font=("Arial", 10), bg="#8B0000", fg="white").grid(row=1, column=1, pady=10)
    
    main_ui.mainloop()

# ---------- LOGIN WINDOW ----------
login_root = tk.Tk()
login_root.title("Login")
login_root.geometry("350x250")
login_root.configure(bg="#f4f4f4")
frame = tk.Frame(login_root, bg="white", padx=20, pady=20)
frame.pack(pady=20)
tk.Label(frame, text="Login", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
tk.Label(frame, text="Username:", font=("Arial", 10), bg="white").pack()
entry_username = tk.Entry(frame, width=25)
entry_username.pack(pady=5)
tk.Label(frame, text="Password:", font=("Arial", 10), bg="white").pack()
entry_password = tk.Entry(frame, width=25, show="*")
entry_password.pack(pady=5)
tk.Button(frame, text="Login", command=login, font=("Arial", 10), bg="#28A745", fg="white").pack(pady=10)
login_root.mainloop()
