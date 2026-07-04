import asyncio
import json
from google import genai

async def test_all_models():
    client = genai.Client(
        api_key=json.load(open('config/api_keys.json', 'r'))['gemini_api_key'], 
        http_options={'api_version': 'v1beta'}
    )
    models = client.models.list()
    flash_models = [m.name for m in models if m.name and 'flash' in m.name.lower()]
    print("Testing models:", flash_models)
    
    for m in flash_models:
        print(f"Testing {m}...")
        try:
            async with client.aio.live.connect(model=m) as session:
                print(f'SUCCESS! {m} works!')
                return
        except Exception as e:
            print(f'Failed {m}: {str(e)}')

asyncio.run(test_all_models())
