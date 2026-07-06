import sounddevice as sd
import vosk
import sys
import json
import queue

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def main():
    print("=== Microphone Tester ===")
    print("Available input devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            default_marker = " (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"[{i}] {dev['name']}{default_marker}")
            
    print("\n")
    device_id_str = input("Enter the device ID to test (or press Enter for default): ")
    
    if device_id_str.strip():
        device_id = int(device_id_str.strip())
    else:
        device_id = sd.default.device[0]
        
    device_info = sd.query_devices(device_id, 'input')
    print(f"\nUsing device: {device_info['name']}")

    print("Loading voice model...")
    model = vosk.Model("voice_activation/vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    print("\n--- Listening... Please say something (Press Ctrl+C to stop) ---")
    try:
        with sd.RawInputStream(
            samplerate=16000, 
            blocksize=8000, 
            device=device_id, 
            dtype='int16', 
            channels=1, 
            callback=callback
        ):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    if res.get("text"):
                        print(f"I heard: {res['text']}")
                else:
                    res = json.loads(recognizer.PartialResult())
                    if res.get("partial"):
                        print(f"Partial: {res['partial']}", end="\r")
    except KeyboardInterrupt:
        print("\nTest stopped.")
    except Exception as e:
        print(f"\nError using this microphone: {e}")

if __name__ == "__main__":
    main()
