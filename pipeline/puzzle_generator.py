import os
import json
import random
import requests
from pipeline.config import GEMINI_API_KEY

HISTORY_FILE = "history.json"

HARD_FALLBACK_PUZZLES = [
    {
        "theme": "Dense Steampunk Clockwork Machinery",
        "target_object": "Antique Brass Skeleton Key",
        "hook": "⚠️ HARD: ONLY 0.1% CAN SPOT IT!",
        "question": "FIND THE HIDDEN BRASS KEY IN 10s!",
        "prompt": "An overwhelmingly dense, intricate wall of thousands of rotating interlocking brass gears, copper cogs, bronze springs, vintage clock faces and pendulum levers. A tiny antique brass skeleton key is flawlessly camouflaged into the metallic gear teeth near the mid-left section, sharing the exact same antique golden-brass patina and metallic luster. Extreme visual complexity, optical illusion, 9:16 vertical orientation",
        "target_location": {"x_pct": 0.38, "y_pct": 0.54, "radius_pct": 0.07},
        "title": "HARD LEVEL: Only 0.1% Spot The Hidden Key! 🗝️🔍 #Shorts #Puzzle #IQTest",
        "description": "Hard difficulty eye test! Can you spot the hidden antique brass key hidden in the clockwork gears before time runs out? Comment YES if you solved it! #puzzle #shorts #riddle #eyetest #hardpuzzle",
        "tags": ["hard puzzle", "hidden object", "brain teaser", "steampunk", "eye test", "iq test", "shorts", "impossible puzzle"]
    },
    {
        "theme": "Winter Snowy Birch Forest",
        "target_object": "Camouflaged White Snowy Owl",
        "hook": "🧠 HARD EYE TEST: 99.9% FAIL!",
        "question": "FIND THE CAMOUFLAGED OWL IN 10s!",
        "prompt": "A dense winter forest of hundreds of slender white birch trees with peeling black and white bark, covered in heavy speckled snow and ice crystals. A white snowy owl with tiny black flecks is perfectly camouflaged perched against a snowy birch trunk in the upper-right section, blending completely into the tree bark pattern. Extreme visual camouflage, photorealistic winter scene, 9:16 vertical",
        "target_location": {"x_pct": 0.68, "y_pct": 0.42, "radius_pct": 0.07},
        "title": "99.9% FAIL! Spot The Camouflaged Snowy Owl 🦉❄️ #Shorts #Puzzle #Hard",
        "description": "Extreme camouflage test! The snowy owl is hiding in plain sight. Can you find it in 10 seconds? #shorts #puzzle #hardpuzzle #eyetest #brainteaser",
        "tags": ["hard puzzle", "hidden object", "camouflage", "snowy owl", "eye test", "shorts", "impossible"]
    },
    {
        "theme": "Autumn Maple Leaf Carpet",
        "target_object": "Sleeping Red Fox",
        "hook": "🔥 EXPERT LEVEL: CAN YOU SPOT IT?",
        "question": "FIND THE SLEEPING FOX IN 10s!",
        "prompt": "A forest ground densely blanketed with tens of thousands of overlapping crisp autumn leaves in shades of burnt orange, deep red, gold, and russet brown. Curled up tightly among the leaves near the lower-center section is a tiny sleeping red fox whose fur matches the exact color, curl, and texture of the surrounding maple leaves. Masterful camouflage, intricate nature art, 9:16 vertical",
        "target_location": {"x_pct": 0.48, "y_pct": 0.62, "radius_pct": 0.08},
        "title": "EXPERT LEVEL: Can You Find The Sleeping Fox? 🦊🍂 #Shorts #Puzzle",
        "description": "Hard difficulty nature camouflage puzzle! 99% of people miss the sleeping fox. Did you beat the clock? #puzzle #shorts #brainteaser #hard #eyetest",
        "tags": ["hard puzzle", "hidden object", "fox", "camouflage", "brain teaser", "shorts", "riddle"]
    }
]

PROMPT = """
You are an expert puzzle and brain-teaser designer specializing in HARD to EXPERT difficulty "Find the Hidden Object" optical illusion challenges.

DIFFICULTY LEVEL: HARD TO EXPERT
The challenge must be genuinely difficult:
1. Dense, intricate visual environment with dozens of confusing distractor patterns and overlapping textures (e.g. Steampunk gear clockwork, dense winter birch trees, crowded mosaic bazaar, speckled coral reef, autumn leaf carpet, intricate floral tapestry).
2. The hidden target object must be perfectly camouflaged, sharing the EXACT same color palette, texture, and geometric style as the background.
3. Target size must be COMPACT (radius_pct: 0.06 to 0.08).
4. Coordinates:
   - x_pct: float between 0.30 and 0.70 (non-obvious, natural spot)
   - y_pct: float between 0.38 and 0.68 (safe zone)
   - radius_pct: float between 0.06 and 0.08 (small, precise highlight)
5. Hook: Urgency hook emphasizing high difficulty (e.g. "⚠️ HARD: ONLY 0.1% CAN SPOT IT!", "🧠 99.8% FAIL THIS TEST!", "🔥 EXPERT EYE TEST (DIFFICULT)").
6. Question: Direct uppercase challenge (e.g. "FIND THE HIDDEN BRASS KEY IN 10s!").

Recently used themes to avoid repeating:
{history_text}

Return ONLY a JSON object with this schema:
{{
  "theme": "Theme Name",
  "target_object": "Object Name",
  "hook": "HOOK TEXT (UPPERCASE)",
  "question": "QUESTION TEXT (UPPERCASE)",
  "prompt": "Detailed AI image prompt, dense camouflage, intricate patterns, 9:16 vertical",
  "target_location": {{"x_pct": 0.45, "y_pct": 0.55, "radius_pct": 0.07}},
  "title": "Viral Click-Worthy Title With Emojis #Shorts #Puzzle #Hard",
  "description": "Engaging description asking viewers to comment if they found it.",
  "tags": ["hard puzzle", "hidden object", "brain teaser", "eye test", "shorts", "riddle", "iq test"]
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
        choice = random.choice(HARD_FALLBACK_PUZZLES)
        save_history(choice["theme"])
        return choice
        
    models = ["gemini-3-flash-preview", "gemini-flash-lite-latest"]
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        formatted_prompt = PROMPT.format(history_text=history_text)
        payload = {
            "contents": [{"parts": [{"text": formatted_prompt}]}],
            "generationConfig": {"temperature": 0.85, "response_mime_type": "application/json"}
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                puzzle = json.loads(text)
                print(f"[Puzzle - HARD] Generated via {model_name}: '{puzzle.get('theme')}' -> Target: '{puzzle.get('target_object')}'")
                save_history(puzzle.get("theme"))
                return puzzle
            else:
                print(f"[Puzzle] Model {model_name} notice {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"[Puzzle] Model {model_name} exception: {e}")
        
    choice = random.choice(HARD_FALLBACK_PUZZLES)
    save_history(choice["theme"])
    return choice
