import socket
import threading
import datetime
import os
import re
import shutil
import time
import platform
import sys

LOG_DIR = "C:/pos-journal-logger"
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")
PORT = 9100

# Workstation IP Addresses for primary and backup printers

PRINTER_MAP = {
    "192.168.1.79": {
        "primary": "192.168.1.220",
        "fallback": "192.168.1.221"
    },
    "192.168.1.14": {
        "primary": "192.168.1.230",
        "fallback": "192.168.1.231"
    },
}
# Workstation Names that will be used when writing the journal logs - Ex: (PCWS01.txt)
# If for any reason a name is not specified, it will export as (workstation ip.txt)

WORKSTATION_NAMES = {
    "192.168.1.79": "PCWS01",
    "192.168.1.14": "PCWS02",
}

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def strip_escpos(data: bytes) -> str:
    clean = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    clean = re.sub(rb'\x1b[@-Z\\\^_`{|}~]', b'', clean)
    clean = re.sub(rb'\x1d[@-Z\\\^_`{|}~]', b'', clean)
    clean = re.sub(rb'\x1b.', b'', clean)
    clean = re.sub(rb'\x1d.', b'', clean)
    clean = re.sub(rb'\x10\x04[\x01-\x04]', b'', clean)
    clean = re.sub(rb'[^\x09\x0A\x20-\x7E]', b'', clean)
    clean = re.sub(rb'\n1(?=Scan with phone camera to pay)', b'\n', clean)
    clean = re.sub(rb'\(k1[A-Z0-9]*', b'', clean)
    clean = re.sub(rb'\(kC\d+P0', b'', clean)
    clean = re.sub(rb'\(k1Q0', b'', clean)
    clean = re.sub(rb'0[*!0][^P]+Please scan the code to pay', b'Please scan the code to pay', clean)
    clean = re.sub(rb'\n1\n(?=Total)', b'\n', clean)
    clean = re.sub(rb'Scan with phone camera to pay\s*0', b'Scan with phone camera to pay', clean)
    clean = re.sub(rb'k1A2k1Ck1E2kC1P0', b'', clean)
    return clean.decode('utf-8', errors='replace')

def send_to_printer(printer_ip, data):
    try:
        with socket.create_connection((printer_ip, PORT), timeout=3) as s:
            s.sendall(data)
        return True, ""
    except Exception as e:
        error_msg = f"[!] Failed to send to printer at {printer_ip}: {e}...going to backup"
        print(error_msg)
        return False, error_msg

def save_job(data, client_ip):
    now = datetime.datetime.now()
    WORKSTATION_NAMES = {
        "192.168.1.79": "PCWS01",
        "192.168.1.14": "PCWS02",
        # Add more workstation names above - this is how the journal logs are named.
    }

    workstation_name = WORKSTATION_NAMES.get(client_ip, client_ip.replace(".", "_"))
    filename = f"{workstation_name}.txt"
    file_path = os.path.join(LOG_DIR, filename)

    cleaned = strip_escpos(data)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 40}\n")
        f.write(f"--- New Print Job [{now.strftime('%H:%M:%S')}] ---\n")
        f.write(cleaned)
        f.write("\n")

    mapping = PRINTER_MAP.get(client_ip)
    printed = False

    if mapping:
        printed, error = send_to_printer(mapping['primary'], data)
        if not printed and 'fallback' in mapping:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {error}\n")

            printed, fallback_error = send_to_printer(mapping['fallback'], data)
            if not printed:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {fallback_error}\n")
                    f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Both primary and backup printers offline.\n")
        elif not printed:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {error}\n")
                f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Primary printer is offline.\n")
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No printer mapping found for {client_ip}.\n")

    print(f"[✔] Saved job to {filename}")

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

def start_emulator(host="0.0.0.0", port=PORT):
    print(f"[LISTENING] Epson emulator listening on {host}:{port}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

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

def check_midnight_and_archive():
    last_checked_day = None
    while True:
        now = datetime.datetime.now()
        if now.day != last_checked_day and now.hour == 0 and now.minute == 0:
            last_checked_day = now.day
            move_logs_to_archive()
            delete_old_archives()
        time.sleep(60)

# Optional: Windows service support
if platform.system() == "Windows":
    try:
        import win32serviceutil
        import win32service
        import win32event

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
else:
    # Linux / macOS
    if __name__ == '__main__':
        threading.Thread(target=check_midnight_and_archive, daemon=True).start()
        start_emulator()
