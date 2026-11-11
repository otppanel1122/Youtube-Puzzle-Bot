import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from pipeline.puzzle_generator import generate_puzzle
from pipeline.image_generator import download_puzzle_image
from pipeline.audio_generator import generate_puzzle_audio
from pipeline.video_renderer import render_puzzle_video
from pipeline.youtube_uploader import upload_puzzle_video
from pipeline.config import OUTPUT_DIR, TEMP_DIR

def run():
    print("=" * 60)
    print("🧩 STARTING VIRAL PUZZLE SHORTS PIPELINE")
    print("=" * 60)
    
    timestamp = int(time.time())
    run_temp_dir = os.path.join(TEMP_DIR, f"puzzle_run_{timestamp}")
    os.makedirs(run_temp_dir, exist_ok=True)
    
    # 1. Generate unique puzzle niche & target
    print("\n[Step 1/4] Selecting Viral Puzzle Niche with Gemini 3.8 Flash...")
    puzzle = generate_puzzle()
    print(f"Theme: {puzzle.get('theme')}")
    print(f"Target Object: {puzzle.get('target_object')}")
    print(f"Hook: {puzzle.get('hook')}")
    print(f"Title: {puzzle.get('title')}")
    
    # 2. Generate high-res puzzle image
    print("\n[Step 2/4] Generating High-Detail Search & Find Visual...")
    image_path = os.path.join(run_temp_dir, "puzzle.jpg")
    download_puzzle_image(puzzle.get("prompt"), image_path)
    
    # 3. Generate Audio (Pure BGM + Ticking Clock + Chime Bell, NO VOICES)
    print("\n[Step 3/4] Synthesizing Clock Ticking & Playful BGM (Zero Human Voice)...")
    audio_path = os.path.join(run_temp_dir, "puzzle_audio.wav")
    generate_puzzle_audio(audio_path, duration=15.0)
    
    # 4. Render 15-second Video with Live Countdown & Answer Reveal
    print("\n[Step 4/4] Rendering 1080x1920 Short with Countdown & Pulsating Answer Ring...")
    output_mp4 = os.path.join(OUTPUT_DIR, f"puzzle_short_{timestamp}.mp4")
    render_puzzle_video(image_path, audio_path, puzzle, output_mp4)
    
    # 5. Upload to Channel 3
    print("\n[Upload] Uploading Puzzle Short to Channel 3...")
    video_url = upload_puzzle_video(
        output_mp4,
        title=puzzle["title"],
        description=puzzle["description"],
        tags=puzzle["tags"]
    )
    
    print("\n" + "=" * 60)
    if video_url:
        print(f"🎉 PUZZLE SHORT PUBLISHED: {video_url}")
    else:
        print(f"✅ Video created at: {output_mp4} (Upload pending credentials)")
    print("=" * 60)

if __name__ == "__main__":
    run()
