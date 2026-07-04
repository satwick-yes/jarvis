import os
import requests
import urllib.parse
from pathlib import Path

def generate_image(parameters: dict, player=None) -> str:
    """
    Generates an image based on a prompt using Pollinations.ai.
    """
    prompt = parameters.get("prompt")
    if not prompt:
        return "Error: No prompt provided for image generation."

    if player:
        player.write_log(f"SYS: Generating image for prompt: '{prompt}'...")

    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            import re
            desktop = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
            safe_prompt = re.sub(r'[\\/*?:"<>|]', "", prompt[:20]).strip()
            filename = f"generated_image_{safe_prompt.replace(' ', '_')}.jpg"
            save_path = os.path.join(desktop, filename)
            
            with open(save_path, "wb") as f:
                f.write(response.content)
                
            if player:
                player.write_log(f"SYS: Image saved to {save_path}")
            
            # Open the image natively
            os.startfile(save_path)
            
            return f"Image successfully generated and saved to {save_path}."
        else:
            return f"Error: Received status code {response.status_code} from image service."
    except Exception as e:
        return f"Error generating image: {e}"
