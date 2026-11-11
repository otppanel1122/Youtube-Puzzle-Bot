import os
import base64
import urllib.parse
import time
import requests
from PIL import Image
from pipeline.config import GEMINI_API_KEY

def try_gemini_image_generation(prompt):
    """
    Attempts to generate high-resolution image using Gemini Pro Image models.
    Requires billing enabled on Google Cloud / AI Studio project.
    """
    if not GEMINI_API_KEY:
        return None
        
    models = ["gemini-3-pro-image", "gemini-2.5-flash-image"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"Generate a high-detail vertical 9:16 illustration of: {prompt}"}]}]
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "inlineData" in p and p["inlineData"].get("data"):
                        print(f"[Image] Successfully generated image via Google Gemini ({model})!")
                        return base64.b64decode(p["inlineData"]["data"])
            elif resp.status_code == 429:
                # Quota limit: 0 indicates project billing not yet attached
                pass
        except Exception as e:
            print(f"[Image] Notice from Gemini image model {model}: {e}")
            
    return None

def download_puzzle_image(prompt, output_path, max_retries=3):
    # 1. Attempt Gemini Pro Image Generation first
    print("[Image] Requesting image from Gemini Pro Image engine...")
    gemini_bytes = try_gemini_image_generation(prompt)
    if gemini_bytes:
        with open(output_path, "wb") as f:
            f.write(gemini_bytes)
        print(f"[Image] Saved Gemini Pro image to {output_path}")
        return output_path
        
    print("[Image] Gemini Image API quota limit 0 (billing not linked); using high-res Flux engine fallback.")
    
    # 2. Enhanced prompt for above-normal to HARD difficulty
    enhanced_prompt = (
        f"{prompt}, extremely dense seek-and-find optical illusion puzzle, "
        "intricate overlapping camouflage patterns, highly detailed textures, "
        "challenging hidden object visual, 9:16 vertical ratio, 8k resolution"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = int(time.time() * 1000) % 1000000
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for attempt in range(max_retries):
        try:
            print(f"[Image] Generating hard puzzle visual (attempt {attempt+1})...")
            resp = requests.get(url, headers=headers, timeout=45)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                with Image.open(output_path) as img:
                    img.verify()
                print(f"[Image] Successfully generated high-difficulty puzzle visual: {output_path}")
                return output_path
        except Exception as e:
            print(f"[Image] Attempt {attempt+1} warning: {e}")
            time.sleep(3)
            
    print("[Image] Creating fallback canvas")
    from PIL import ImageDraw
    fallback = Image.new("RGB", (768, 1344), color=(25, 30, 45))
    draw = ImageDraw.Draw(fallback)
    draw.text((100, 600), "Hard Search & Find Challenge", fill=(255, 255, 255))
    fallback.save(output_path, "JPEG")
    return output_path
