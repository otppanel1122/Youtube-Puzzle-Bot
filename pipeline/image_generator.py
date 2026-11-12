import os
import base64
import urllib.parse
import time
import subprocess
import requests
from PIL import Image
from pipeline.config import GEMINI_API_KEY

def try_puter_image_generation(prompt, output_path):
    token = os.getenv("PUTER_AUTH_TOKEN")
    if not token:
        return False
        
    script_path = os.path.join(os.path.dirname(__file__), "generate_puter.js")
    if not os.path.exists(script_path):
        return False
        
    try:
        print(f"[Image] Generating puzzle visual via Puter.js ({output_path})...")
        res = subprocess.run(
            ["node", script_path, prompt, output_path],
            capture_output=True,
            text=True,
            timeout=45,
            env={**os.environ, "PUTER_AUTH_TOKEN": token}
        )
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
            with Image.open(output_path) as img:
                img.verify()
            print(f"[Image] Successfully generated puzzle visual via Puter.js!")
            return True
        else:
            print(f"[Image] Puter.js notice: {res.stdout.strip()} | {res.stderr.strip()}")
    except Exception as e:
        print(f"[Image] Puter call notice: {e}")
    return False

def try_gemini_image_generation(prompt):
    if not GEMINI_API_KEY:
        return None
        
    models = ["gemini-3-pro-image", "gemini-2.5-flash-image"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"Generate a high-detail vertical 9:16 illustration of: {prompt}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]}
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
        except Exception:
            pass
    return None

def download_puzzle_image(prompt, output_path, max_retries=3):
    # 1. Try Puter.js first
    if try_puter_image_generation(prompt, output_path):
        return output_path

    # 2. Try Gemini Pro Image
    gemini_bytes = try_gemini_image_generation(prompt)
    if gemini_bytes:
        with open(output_path, "wb") as f:
            f.write(gemini_bytes)
        print(f"[Image] Saved Gemini Pro image to {output_path}")
        return output_path
        
    # 3. High-res Flux fallback
    enhanced_prompt = (
        f"{prompt}, extremely dense seek-and-find optical illusion puzzle, "
        "intricate overlapping camouflage patterns, highly detailed textures, "
        "challenging hidden object visual, 9:16 vertical ratio, 8k resolution"
    )
    encoded = urllib.parse.quote(enhanced_prompt)
    seed = int(time.time() * 1000) % 1000000
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true&seed={seed}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for attempt in range(max_retries):
        try:
            print(f"[Image] Generating hard puzzle visual (attempt {attempt+1})...")
            resp = requests.get(url, headers=headers, timeout=40)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                with Image.open(output_path) as img:
                    img.verify()
                print(f"[Image] Successfully generated high-difficulty puzzle visual: {output_path}")
                return output_path
            elif resp.status_code == 402:
                print(f"[Image] Pollinations rate limit (HTTP 402).")
                break
        except Exception as e:
            print(f"[Image] Attempt {attempt+1} warning: {e}")
            time.sleep(2)
            
    print("[Image] Creating fallback canvas")
    from PIL import ImageDraw
    fallback = Image.new("RGB", (768, 1344), color=(25, 30, 45))
    fallback.save(output_path, "JPEG")
    return output_path
