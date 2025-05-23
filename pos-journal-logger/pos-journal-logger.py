# Libaries used for this Python project

import socket
import threading
import datetime
import os
import re
import shutil
import time
import platform
import sys

# If statement for linking the correct director if this is a Windows Operating System

if platform.system() == "Windows":
    BASE_DIR = "C:/pos-journal-logger"

# Else statement for linking the correct directory if this is a Linux Operating System

else:
    BASE_DIR = "/pos-journal-logger"

# Log directory function for depicting where to store the logs under the pos-journal-logger directory

LOG_DIR = os.path.join(BASE_DIR, "logs")

# Archive directory function for depicting where to store the archived logs under the logs directory

ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")

# Emulation running on Port 9100 so POS systems are tricked into thinking this is an Epson/POS Receipt printer

PORT = 9100

# Workstation IP Addresses for primary and backup printers

# Add more printers below and tie it to the IP address of the workstation

PRINTER_MAP = {
    
    # PCWSO1 IP Address for redirection to main/backup printers
    
    "192.168.100.23": {
        
    # PCWSO1's main receipt printer
        
        "primary": "192.168.100.202",
        
    # PCWSO1's backup receipt printer
        
        "fallback": "192.168.100.221"
    },
    
    # PCWSO2 IP Address for redirection to main/backup printers
    
    "192.168.100.24": {
        
    # PCWSO2's main receipt printer
        
        "primary": "192.168.100.203",
        
    # PCWSO2's backup receipt printer
        
        "fallback": "192.168.100.222"
    },
}

# Workstation Names that will be used when writing the journal logs - Example: (PCWS01.txt)

# If for any reason a name is not specified, it will export as (workstation ip.txt)

WORKSTATION_NAMES = {
    
# PCWS01 Workstation Name
    
    "192.168.100.23": "PCWS01",
    
# PCWS02 Workstation Name
    
    "192.168.100.24": "PCWS02",
}


# Function to ensure the log directory exists

os.makedirs(LOG_DIR, exist_ok=True)

# Function to ensure the archive directory exists

os.makedirs(ARCHIVE_DIR, exist_ok=True)

# The strip_escpos function uses clean to replace the extra unncessary data and output a clean log file 

# This will likely need to be adjusted on a per site basis

def strip_escpos(data: bytes) -> str:
    clean = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    clean = re.sub(rb'\x1b[@-Z\\\^_`{|}~]', b'', clean)
    clean = re.sub(rb'\x1d[@-Z\\\^_`{|}~]', b'', clean)
    clean = re.sub(rb'\x1b.', b'', clean)
    clean = re.sub(rb'\x1d.', b'', clean)
    clean = re.sub(rb'\x10\x04[\x01-\x04]', b'', clean)
    clean = re.sub(rb'[^\x09\x0A\x20-\x7E]', b'', clean)
    # Custom binary substitutions
    clean = re.sub(rb'k1A2k1Ck1E2k\[1P0', b'', clean)
    clean = re.sub(rb'\nKZ800-1\n?', b'\n', clean)
    decoded = clean.decode('utf-8', errors='replace')
    lines = decoded.splitlines()
    cleaned_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        # Truncate SpotOn link and skip next gibberish line
        if "https://order.spoton.com/pay/" in line:
            cleaned_lines.append(line[:88])
            if i + 1 < len(lines) and not lines[i + 1].startswith("Customer copy"):
                skip_next = True
            continue
        # Remove "1" prefix from "Pay With Cash:"
        if line.strip().startswith("1Pay With Cash:"):
            cleaned_lines.append("Pay With Cash:" + line.strip()[16:])
            continue
        # Remove "1" prefix from "Scan with phone camera to pay"
        if line.strip().startswith("1Scan with phone camera to pay"):
            cleaned_lines.append("Scan with phone camera to pay")
            continue
        # Remove "0" if it directly follows the scan line
        if i > 0 and cleaned_lines[-1].strip() == "Scan with phone camera to pay" and line.strip() == "0":
            continue
        # Remove lone "1" after Sales Tax
        if i > 0 and "Sales Tax" in lines[i - 1] and line.strip() == "1":
            continue
        cleaned_lines.append(line[:88])
    return '\n'.join(cleaned_lines)

# This function defines sending to the backup printer. If it fails, it will go to the backup

def send_to_printer(printer_ip, data):
    try:
        with socket.create_connection((printer_ip, PORT), timeout=3) as s:
            s.sendall(data)
        return True, ""

# This depicts the error message output inside of the log for when it goes to the backup printer
    
    except Exception as e:
        error_msg = f"[!] Failed to send to printer at {printer_ip}: {e}...going to backup"
        print(error_msg)
        return False, error_msg

# This is the function used for saving the log file names and resolve it to the name of the workstation instead of an IP address

def save_job(data, client_ip):
    now = datetime.datetime.now()
    WORKSTATION_NAMES = {
        
# Name Resolution for the IP Address of PCWS01
        
        "192.168.100.23": "PCWS01",
        
# Name Resolution for the IP Address of PCWS02

        "192.168.1.14": "PCWS02",

# Add more workstation names above - this is how the journal logs are named.

    }

# This is the function for formatting the log file name and exporting it as a text file

    workstation_name = WORKSTATION_NAMES.get(client_ip, client_ip.replace(".", "_"))
    filename = f"{workstation_name}.txt"
    file_path = os.path.join(LOG_DIR, filename)
    
# This is calling the strip_escpos clean function to export the log and import the New Print Job with the date and time
    
    cleaned = strip_escpos(data)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 40}\n")
        f.write(f"--- New Print Job [{now.strftime('%H:%M:%S')}] ---\n")
        f.write(cleaned)
        f.write("\n")

# This is the function used to get the Printer Map and send it to the primary, then to the backup
    
    mapping = PRINTER_MAP.get(client_ip)
    printed = False
    
# This is the section used to write the error if it is unable to send to the primary, it will go to the backup printer
    
    if mapping:
        printed, error = send_to_printer(mapping['primary'], data)
        if not printed and 'fallback' in mapping:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {error}\n")
                
# This is the section used to depict that both the primary and backup printers are offline
            
            printed, fallback_error = send_to_printer(mapping['fallback'], data)
            if not printed:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {fallback_error}\n")
                    f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Both primary and backup printers offline.\n")
                    
# This is the section used to write the error 
        
        elif not printed:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {error}\n")
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Primary printer is offline.\n")

# This is the section used to write the error if a printer mapping was not found for the workstation ip set in the printer map
    
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No printer mapping found for {client_ip}.\n")

    print(f"[✔] Saved job to {filename}")

# This is the section used to write the error if a printer has been disconnected or if the connection was reset

def handle_client(conn, addr):
    client_ip = addr[0]
    print(f"[CONNECTED] {client_ip}")
    data = bytearray()
    try:
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            if chunk in (b'\x10\x04\x01', b'\x10\x04\x02', b'\x10\x04\x04'):
                conn.sendall(b'\x12' if chunk == b'\x10\x04\x01' else b'\x00')
            else:
                data.extend(chunk)
    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {client_ip}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {client_ip}")
        if data:
            save_job(data, client_ip)

# Emulation task to run on the IP address of the host machine

# Example: If the machine's IP address is 192.168.100.200, 

# then that will be the IP address of the dummy printer you create in your POS system to tell the Workstations/clients to print to

def start_emulator(host="0.0.0.0", port=PORT):
    print(f"[LISTENING] Epson emulator listening on {host}:{port}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Function used to move logs to the archive directory

def move_logs_to_archive():
    today = datetime.datetime.now().strftime('%m-%d-%Y')
    archive_folder = os.path.join(ARCHIVE_DIR, today)
    os.makedirs(archive_folder, exist_ok=True)

    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".txt"):
            src = os.path.join(LOG_DIR, filename)
            dst = os.path.join(archive_folder, filename)
            shutil.move(src, dst)

    print(f"[✔] Moved logs to archive folder: {today}")

# Function used to check if the archive folders are older than 90 days and delete them if they are

# You can increase or decrease the amount of days depending on the use case

def delete_old_archives():
    now = datetime.datetime.now()
    for folder_name in os.listdir(ARCHIVE_DIR):
        folder_path = os.path.join(ARCHIVE_DIR, folder_name)
        if os.path.isdir(folder_path):
            try:
                folder_date = datetime.datetime.strptime(folder_name, '%m-%d-%Y')
                if (now - folder_date).days > 90:
                    shutil.rmtree(folder_path)
                    print(f"[✔] Deleted old archive folder: {folder_name}")
            except ValueError:
                pass

# Function used to check if it is midnight then archive all of the logs to the current date and time

def check_midnight_and_archive():
    last_checked_day = None
    while True:
        now = datetime.datetime.now()
        if now.day != last_checked_day and now.hour == 0 and now.minute == 0:
            last_checked_day = now.day
            move_logs_to_archive()
            delete_old_archives()
        time.sleep(60)

# Windows service support & usaged of win32 function

if platform.system() == "Windows":
    try:
        import win32serviceutil
        import win32service
        import win32event
        
# Windows service name and display name
        
        class EpsonEmulatorService(win32serviceutil.ServiceFramework):
            _svc_name_ = "pos-journal-logger"
            _svc_display_name_ = "pos-journal-logger"

            def __init__(self, args):
                win32serviceutil.ServiceFramework.__init__(self, args)
                self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
                self.running = True

            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                self.running = False
                win32event.SetEvent(self.hWaitStop)

            def SvcDoRun(self):
                threading.Thread(target=check_midnight_and_archive, daemon=True).start()
                start_emulator()

        if __name__ == '__main__' and len(sys.argv) > 1:
            win32serviceutil.HandleCommandLine(EpsonEmulatorService)
        elif __name__ == '__main__':
            # Running as normal script
            threading.Thread(target=check_midnight_and_archive, daemon=True).start()
            start_emulator()

    except ImportError:
        print("[!] pywin32 is not installed. Windows service support is disabled.")
        if __name__ == '__main__':
            threading.Thread(target=check_midnight_and_archive, daemon=True).start()
            start_emulator()

# Linux systemd service support

else:
    # Linux / macOS
    if __name__ == '__main__':
        threading.Thread(target=check_midnight_and_archive, daemon=True).start()
        start_emulator()
