import asyncio
import os
import json
from google import genai
import main
from ui import JarvisUI
import tkinter as tk

async def test_connect():
    client = genai.Client(
        api_key=main._get_api_key(),
        http_options={"api_version": "v1beta"}
    )
    root = tk.Tk()
    config = main.JarvisLive(JarvisUI(root))._build_config()
    print("Connecting...")
    try:
        async with client.aio.live.connect(model='models/gemini-2.5-flash-native-audio-latest', config=config) as session:
            print("Connected!")
            await session.send(input="say hello", end_of_turn=True)
            print("Message sent!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_connect())
