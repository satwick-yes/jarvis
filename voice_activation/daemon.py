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
    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
    listener_path = str(BASE_DIR / "voice_activation" / "listener.py")
    
    while True:
        if is_jarvis_running():
            time.sleep(2)
        else:
            subprocess.run([pythonw_path, listener_path], cwd=str(BASE_DIR))
            time.sleep(2)

if __name__ == "__main__":
    main()
