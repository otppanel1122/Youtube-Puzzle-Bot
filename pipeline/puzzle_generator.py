import os
import json
import random
import requests
from pipeline.config import GEMINI_API_KEY

HISTORY_FILE = "history.json"

FALLBACK_PUZZLES = [
    {
        "theme": "Cozy Vintage Bookstore",
        "target_object": "Sleeping Ginger Cat",
        "hook": "🧠 99% OF PEOPLE FAIL!",
        "question": "FIND THE SLEEPING CAT IN 10 SECONDS!",
        "prompt": "An intricate, cozy vintage library and bookstore with towering wooden bookshelves overflowing with antique books, warm golden lighting, a sleeping ginger orange tabby cat cleverly hidden among the colorful book stacks on a middle shelf, highly detailed, whimsical storybook art, vibrant colors, 9:16 vertical",
        "target_location": {"x_pct": 0.58, "y_pct": 0.48, "radius_pct": 0.12},
        "title": "Can You Find The Hidden Cat In 10 Seconds? 🐱🔍 #Shorts #Puzzle #BrainTeaser",
        "description": "Test your eyesight and brain power! Can you find the hidden cat before the timer ends? Comment YES if you found it! #shorts #puzzle #riddle #brainteaser #hiddenobject",
        "tags": ["puzzle", "hidden object", "brain teaser", "find the cat", "iq test", "mind game", "shorts", "riddle"]
    },
    {
        "theme": "Enchanted Fairy Forest",
        "target_object": "Baby Forest Dragon",
        "hook": "🔥 ONLY 1% CAN SPOT IT!",
        "question": "FIND THE BABY DRAGON IN 10 SECONDS!",
        "prompt": "A magical glowing enchanted forest with giant luminescent mushrooms, mossy ancient trees, glowing fireflies, a tiny green baby dragon camouflaged among the lush tree branches and glowing foliage, extremely detailed fantasy digital painting, vibrant magical atmosphere, 9:16 vertical",
        "target_location": {"x_pct": 0.42, "y_pct": 0.52, "radius_pct": 0.12},
        "title": "Only 1% Can Spot The Hidden Dragon! 🐉🔍 #Shorts #Puzzle #IQTest",
        "description": "Spot the hidden baby dragon before the clock hits zero! Did you beat the clock? #puzzle #shorts #brainteaser #hiddenobject #riddle",
        "tags": ["puzzle", "hidden object", "dragon", "brain teaser", "riddles", "shorts", "iq test"]
    },
    {
        "theme": "Underwater Coral Reef",
        "target_object": "Golden Crown Seahorse",
        "hook": "⚡ EYE TEST FOR GENIUSES!",
        "question": "FIND THE GOLDEN SEAHORSE IN 10s!",
        "prompt": "A vibrant underwater tropical coral reef teeming with schools of colorful clownfish, sea anemones, glowing jellyfish, a tiny glowing golden seahorse expertly camouflaged near the sea plants in the reef, ultra detailed, bright oceanic colors, 9:16 vertical",
        "target_location": {"x_pct": 0.65, "y_pct": 0.56, "radius_pct": 0.12},
        "title": "Spot The Hidden Golden Seahorse In 10s! 🌊🔍 #Shorts #Puzzle",
        "description": "99% of people miss this! Can you find the golden seahorse before time runs out? #shorts #puzzle #brainteaser #eyetest",
        "tags": ["puzzle", "hidden object", "eye test", "brain teaser", "seahorse", "shorts"]
    }
]

PROMPT = """
You are a viral YouTube Shorts puzzle creator and game designer.
Design a highly engaging, visual "Find the Hidden Object / Eye Test" puzzle for a 15-second YouTube Short.

RULES:
1. Every time, pick a UNIQUE, fascinating visual niche (e.g. Cyberpunk Night Market, Cartoon Penguin Party, Ancient Egyptian Tomb, Candy Wonderland, Autumn Fox Meadow, Medieval Castle Feast, Haunted Attic, Outer Space Station).
2. The hidden object must be specific and naturally camouflaged into the scene.
3. Choose a target location on the 9:16 vertical image where the object should be placed:
   - x_pct: float between 0.25 and 0.75 (horizontal center percentage)
   - y_pct: float between 0.35 and 0.70 (vertical percentage, safe from top and bottom UI)
   - radius_pct: float around 0.10 to 0.14 (size of the highlight circle)
4. Hook text: punchy 3-5 word challenge (e.g. "🧠 99% FAIL THIS TEST!", "⚡ ONLY 1% CAN SPOT IT!", "🔥 EYE TEST FOR GENIUSES!").
5. Question text: clear instruction (e.g. "FIND THE HIDDEN CAT IN 10 SECONDS!").
6. Provide an ultra-detailed image generation prompt describing the dense scene and explicitly placing the camouflaged object around that area.

Recently used themes to avoid repeating:
{history_text}

Return ONLY a JSON object with this schema:
{{
  "theme": "Theme Name",
  "target_object": "Object Name",
  "hook": "HOOK TEXT (UPPERCASE)",
  "question": "QUESTION TEXT (UPPERCASE)",
  "prompt": "Detailed AI image prompt, highly detailed, colorful, 9:16 vertical",
  "target_location": {{"x_pct": 0.60, "y_pct": 0.50, "radius_pct": 0.12}},
  "title": "Viral Click-Worthy Title With Emojis #Shorts #Puzzle #BrainTeaser",
  "description": "Engaging description asking viewers to comment if they found it.",
  "tags": ["puzzle", "hidden object", "brain teaser", "eye test", "shorts", "riddle", "iq test"]
}}
"""

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(theme_title):
    history = load_history()
    history.append(theme_title)
    if len(history) > 40:
        history = history[-40:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

def generate_puzzle():
    history = load_history()
    history_text = "\n".join([f"- {h}" for h in history[-10:]])
    
    if not GEMINI_API_KEY:
        choice = random.choice(FALLBACK_PUZZLES)
        save_history(choice["theme"])
        return choice
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    formatted_prompt = PROMPT.format(history_text=history_text)
    payload = {
        "contents": [{"parts": [{"text": formatted_prompt}]}],
        "generationConfig": {"temperature": 0.9, "response_mime_type": "application/json"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=35)
        if resp.status_code == 200:
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            puzzle = json.loads(text)
            print(f"[Puzzle] Generated Niche: '{puzzle.get('theme')}' -> Find '{puzzle.get('target_object')}'")
            save_history(puzzle.get("theme"))
            return puzzle
        else:
            print(f"[Puzzle] Gemini API notice {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print("[Puzzle] Gemini error, using curated template:", e)
        
    choice = random.choice(FALLBACK_PUZZLES)
    save_history(choice["theme"])
    return choice
