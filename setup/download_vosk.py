import urllib.request
import zipfile
import sys
import os
from pathlib import Path

url = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
target_dir = Path(__file__).resolve().parent.parent / "voice_activation"
zip_path = target_dir / "vosk-model-en-in-0.5.zip"
model_dir = target_dir / "vosk-model-en-in-0.5"

if model_dir.exists():
    print(f"Vosk model already exists at {model_dir}")
    sys.exit(0)

target_dir.mkdir(parents=True, exist_ok=True)

def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        sys.stdout.write(f"\rDownloading Vosk Model: {percent:5.1f}% ({readsofar / (1024*1024):.2f} MB / {totalsize / (1024*1024):.2f} MB)")
        sys.stdout.flush()

print(f"Downloading Indian English Voice Model (approx 1 GB) from {url}...")
urllib.request.urlretrieve(url, zip_path, reporthook)
print("\nDownload complete. Extracting...")

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(target_dir)

print("\nExtraction complete. Cleaning up zip file...")
os.remove(zip_path)
print("Vosk model setup complete.")
