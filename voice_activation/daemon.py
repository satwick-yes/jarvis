import time
import subprocess
import psutil
import sys
import os
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class _DummyIO:
    def __init__(self): pass
    def write(self, msg, *args, **kwargs): pass
    def flush(self): pass

if getattr(sys, 'stdout', None) is None: sys.stdout = _DummyIO()
if getattr(sys, 'stderr', None) is None: sys.stderr = _DummyIO()

def is_jarvis_running():
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            name = p.info.get('name')
            if name and 'python' in name.lower():
                cmd = p.info.get('cmdline')
                if cmd and any('main.py' in str(c) for c in cmd):
                    return True
        except:
            pass
    return False

def log_daemon(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

def main():
    python_path = sys.executable.replace("pythonw.exe", "python.exe")
    listener_path = str(BASE_DIR / "voice_activation" / "listener.py")
    
    with open(str(BASE_DIR / "daemon_verbose.log"), "w") as f:
        f.write("=== Daemon Started ===\n")
        
    while True:
        try:
            if is_jarvis_running():
                # log_daemon("Jarvis is running, sleeping...")
                time.sleep(2)
            else:
                log_daemon("Jarvis is NOT running, launching listener...")
                subprocess.run(
                    [python_path, listener_path], 
                    cwd=str(BASE_DIR), 
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                log_daemon("Listener finished, sleeping...")
                time.sleep(2)
        except Exception as e:
            log_daemon(f"ERROR: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
