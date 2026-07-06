import time
import subprocess
import psutil
import sys
import os
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

def main():
    python_path = sys.executable.replace("pythonw.exe", "python.exe")
    listener_path = str(BASE_DIR / "voice_activation" / "listener.py")
    
    with open(str(BASE_DIR / "daemon_verbose.log"), "w") as f:
        f.write("Daemon started!\n")
        
    while True:
        try:
            with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
                f.write("Checking if Jarvis is running...\n")
                
            if is_jarvis_running():
                with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
                    f.write("Jarvis is running, sleeping...\n")
                time.sleep(2)
            else:
                with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
                    f.write("Jarvis is NOT running, launching listener...\n")
                subprocess.run(
                    [python_path, listener_path], 
                    cwd=str(BASE_DIR), 
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
                    f.write("Listener finished, sleeping...\n")
                time.sleep(2)
        except Exception as e:
            with open(str(BASE_DIR / "daemon_verbose.log"), "a") as f:
                f.write("ERROR: " + str(e) + "\n")
            time.sleep(2)

if __name__ == "__main__":
    main()
