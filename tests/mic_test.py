import sounddevice as sd
import numpy as np

print("Testing mic...")
try:
    recording = sd.rec(int(16000 * 2), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    rms = np.sqrt(np.mean(recording.astype(np.float32)**2))
    print(f"Mic RMS Volume: {rms}")
    if rms < 10:
        print("WARNING: Microphone is completely silent! Audio driver might be glitched.")
    else:
        print("Microphone is capturing audio fine.")
except Exception as e:
    print(f"Mic error: {e}")
