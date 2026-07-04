import asyncio
import json
from google import genai

async def test_conn():
    client = genai.Client(
        api_key=json.load(open('config/api_keys.json', 'r'))['gemini_api_key'], 
        http_options={'api_version': 'v1beta'}
    )
    try:
        async with client.aio.live.connect(model='gemini-2.0-flash-exp') as session:
            print('Connected successfully!')
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('Error connecting:', str(e))

asyncio.run(test_conn())
