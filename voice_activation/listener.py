import os
import sys

class _DummyIO:
    def __init__(self):
        pass
    def write(self, msg, *args, **kwargs):
        pass
    def flush(self):
        pass

if getattr(sys, 'stdout', None) is None:
    sys.stdout = _DummyIO()
if getattr(sys, 'stderr', None) is None:
    sys.stderr = _DummyIO()

import json
import time
import subprocess
import threading
from pathlib import Path
import psutil
import sounddevice as sd
import vosk

# Ensure correct base dir
def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
VA_DIR = BASE_DIR / "voice_activation"
LOG_PATH = VA_DIR / "activation.log"

def log_msg(msg: str):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

def clear_log():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("=== Background Voice Activation Log Started ===\n")
    except:
        pass

def is_jarvis_running():
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            name = p.info.get('name')
            if name and 'python' in name.lower():
                cmd = p.info.get('cmdline')
                if cmd and any('main.py' in str(c) for c in cmd):
                    return True
        except Exception:
            pass
    return False

def launch_jarvis():
    if is_jarvis_running():
        return
    log_msg("Launching Jarvis UI (no console)...")
    
    try:
        python_path = sys.executable.replace("pythonw.exe", "python.exe")
        subprocess.Popen(
            [python_path, "main.py"], 
            cwd=str(BASE_DIR), 
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log_msg("Jarvis spawned. Listener exiting...")
        os._exit(0)
    except Exception as e:
        log_msg(f"Failed to launch Jarvis: {e}")

def setup_vosk():
    vosk.SetLogLevel(-1)
    model_dir = VA_DIR / "vosk-model-small-en-us-0.15"
    if not model_dir.exists():
        log_msg("Vosk model not found. Please ensure it was extracted.")
        sys.exit(1)
    
    model = vosk.Model(str(model_dir))
    return vosk.KaldiRecognizer(model, 16000)

def main():
    clear_log()
    log_msg("Initializing background listener...")
    
    device_name = sd.query_devices(sd.default.device[0], 'input')['name']
    log_msg(f"Using default device: {device_name}")
    
    recognizer = setup_vosk()
    
    log_msg("Waiting for wake word in background...")
    
    import queue
    q = queue.Queue()
    
    def callback(indata, frames, time_info, status):
        if status:
            pass 
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            blocksize=8000,
            callback=callback
        ):
            log_msg("Listening stream active...")
            while True:
                data = q.get()
                
                try:
                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        text = res.get("text", "").lower()
                        if text:
                            log_msg(f"Recognized: {text}")
                        if "jarvis" in text:
                            log_msg(f"Wake word matched in full result: {text}")
                            threading.Thread(target=launch_jarvis).start()
                    else:
                        res = json.loads(recognizer.PartialResult())
                        text = res.get("partial", "").lower()
                        if "jarvis" in text:
                            log_msg(f"Wake word matched in partial result: {text}")
                            threading.Thread(target=launch_jarvis).start()
                            # Flush the queue to avoid immediate double-triggering
                            while not q.empty():
                                try: q.get_nowait()
                                except: pass
                            time.sleep(2)
                except Exception as e:
                    log_msg(f"Processing error: {e}")
    except Exception as e:
        log_msg(f"Listener stream error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open(str(VA_DIR / "listener_error.log"), "a") as f:
            f.write(traceback.format_exc() + "\n")
