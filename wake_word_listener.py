import speech_recognition as sr
import subprocess
import time
import os
import sys
import datetime

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, "listener.log")
    
    # Clear log on PC restart using boot time
    import psutil
    boot_time_file = os.path.join(script_dir, "boot_time.txt")
    current_boot_time = psutil.boot_time()
    
    clear_log = False
    if os.path.exists(boot_time_file):
        try:
            with open(boot_time_file, "r") as f:
                saved_boot_time = f.read().strip()
            if saved_boot_time != str(current_boot_time):
                clear_log = True
        except Exception:
            clear_log = True
    else:
        clear_log = True
        
    if clear_log:
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("")
            with open(boot_time_file, "w") as f:
                f.write(str(current_boot_time))
        except Exception:
            pass
            
    # Redirect print statements to a log file for debugging
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a", encoding="utf-8")
        def write(self, message):
            if self.terminal:
                self.terminal.write(message)
            self.log.write(message)
            self.log.flush()
        def flush(self):
            if self.terminal:
                self.terminal.flush()
            self.log.flush()
            
    sys.stdout = Logger(log_file)
    sys.stderr = sys.stdout

    r = sr.Recognizer()
    m = sr.Microphone()

    print(f"\n--- {datetime.datetime.now()} ---")
    print("Initializing wake word listener...")
    # Adjust for ambient noise
    with m as source:
        r.adjust_for_ambient_noise(source, duration=2)
        r.dynamic_energy_threshold = False
        if r.energy_threshold < 300:
            r.energy_threshold = 300
    print(f"Energy threshold set to: {r.energy_threshold}")

    print("Wake word listener started. Say 'jarvis turn on' or 'jarvis wake up' to wake Jarvis.")
    
    
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = "pythonw"

    import psutil
    
    def is_main_running():
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

    while True:
        try:
            if is_main_running():
                time.sleep(2)
                continue
                
            with m as source:
                # Listen for short phrases
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
            
            text = r.recognize_google(audio, language='en-IN').lower()
            print(f"[{datetime.datetime.now().time()}] Heard: {text}")
            
            # Highly flexible wake word detection (catches just the name or mishearings)
            wake_words = ["jarvis", "jervis", "tarvis", "travis", "darvis", "charvis", "javed", "service"]
            if any(word in text for word in wake_words):
                print("Wake word detected! Launching Jarvis Console...")
                # Launch Jarvis in the background silently
                subprocess.Popen([pythonw_exe, "main.py"], cwd=script_dir)
                # Sleep to prevent launching it multiple times immediately
                time.sleep(10)
                
        except sr.WaitTimeoutError:
            # Re-enter the loop and listen again
            print(f"[{datetime.datetime.now().time()}] Listen timeout, restarting loop...")
            pass
        except sr.UnknownValueError:
            print(f"[{datetime.datetime.now().time()}] Speech was unintelligible")
            pass
        except sr.RequestError as e:
            print(f"[{datetime.datetime.now().time()}] API Error: Could not request results from Google Speech Recognition service; {e}")
            time.sleep(5)
        except Exception as e:
            print(f"[{datetime.datetime.now().time()}] Unexpected error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
