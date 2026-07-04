import speech_recognition as sr
import subprocess
import time
import os
import sys

def main():
    r = sr.Recognizer()
    m = sr.Microphone()

    print("Initializing wake word listener...")
    # Adjust for ambient noise
    with m as source:
        r.adjust_for_ambient_noise(source, duration=2)

    print("Wake word listener started. Say 'jarvis turn on' to wake Jarvis.")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(script_dir, "start_jarvis.bat")

    while True:
        try:
            with m as source:
                # Listen for short phrases (up to 3 seconds)
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
            
            text = r.recognize_google(audio).lower()
            print(f"Heard: {text}")
            
            if "jarvis" in text and "turn on" in text:
                print("Wake word detected! Launching Jarvis...")
                # Launch jarvis in a new console window so the user can interact with it
                subprocess.Popen([bat_path], cwd=script_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
                # Sleep to prevent launching it multiple times immediately
                time.sleep(10)
                
        except sr.WaitTimeoutError:
            # Re-enter the loop and listen again
            pass
        except sr.UnknownValueError:
            # Speech was unintelligible
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
