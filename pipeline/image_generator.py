import os
import urllib.parse
import time
import requests
from PIL import Image

def download_puzzle_image(prompt, output_path, max_retries=3):
    enhanced_prompt = f"{prompt}, intricate search and find illustration, rich vibrant colors, high resolution, 9:16 vertical orientation"
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = int(time.time() * 1000) % 1000000
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for attempt in range(max_retries):
        try:
            print(f"[Image] Generating puzzle image (attempt {attempt+1})...")
            resp = requests.get(url, headers=headers, timeout=45)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                with Image.open(output_path) as img:
                    img.verify()
                print(f"[Image] Successfully generated puzzle image: {output_path}")
                return output_path
        except Exception as e:
            print(f"[Image] Attempt {attempt+1} warning: {e}")
            time.sleep(3)
            
    print("[Image] Creating clean fallback puzzle canvas")
    from PIL import ImageDraw
    fallback = Image.new("RGB", (768, 1344), color=(25, 30, 45))
    draw = ImageDraw.Draw(fallback)
    draw.text((100, 600), "Search & Find Challenge", fill=(255, 255, 255))
    fallback.save(output_path, "JPEG")
    return output_path
