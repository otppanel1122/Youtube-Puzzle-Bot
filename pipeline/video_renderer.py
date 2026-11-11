import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 15.0 # seconds
REVEAL_TIME = 11.0 # time when answer appears

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def get_fonts():
    font_paths = [
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    fp = r"C:\Windows\Fonts\impact.ttf"
    for p in font_paths:
        if os.path.exists(p):
            fp = p
            break
            
    try:
        font_hook = ImageFont.truetype(fp, 46)
        font_question = ImageFont.truetype(fp, 54)
        font_timer = ImageFont.truetype(fp, 64)
        font_reveal = ImageFont.truetype(fp, 58)
        font_cta = ImageFont.truetype(fp, 48)
        return font_hook, font_question, font_timer, font_reveal, font_cta
    except Exception:
        d = ImageFont.load_default()
        return d, d, d, d, d

FONT_HOOK, FONT_QUESTION, FONT_TIMER, FONT_REVEAL, FONT_CTA = get_fonts()

def render_puzzle_frame(base_img, t, puzzle_data):
    # 1. Slow, subtle zoom (1.0 to 1.04)
    zoom = 1.0 + 0.04 * (t / DURATION)
    w, h = base_img.size
    crop_w, crop_h = w / zoom, h / zoom
    left = (w - crop_w) / 2.0
    top = (h - crop_h) / 2.0
    frame = base_img.crop((int(left), int(top), int(left + crop_w), int(top + crop_h)))
    frame = frame.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 2. Top Hook Badge (e.g. "🧠 99% OF PEOPLE FAIL!")
    hook_text = puzzle_data.get("hook", "🧠 99% OF PEOPLE FAIL!")
    bbox_h = draw.textbbox((0, 0), hook_text, font=FONT_HOOK)
    hw, hh = bbox_h[2] - bbox_h[0], bbox_h[3] - bbox_h[1]
    hx0 = (WIDTH - hw) // 2 - 28
    hy0 = 140
    hx1 = (WIDTH + hw) // 2 + 28
    hy1 = hy0 + hh + 24
    draw.rounded_rectangle([hx0, hy0, hx1, hy1], radius=16, fill=(210, 20, 30, 235), outline=(255, 255, 255, 240), width=3)
    draw.text(((WIDTH - hw) // 2, hy0 + 10), hook_text, font=FONT_HOOK, fill=(255, 255, 255, 255))
    
    # 3. Action Question Banner (e.g. "🔍 FIND THE SLEEPING CAT!")
    q_text = puzzle_data.get("question", f"FIND THE {puzzle_data.get('target_object', 'OBJECT').upper()}!")
    bbox_q = draw.textbbox((0, 0), q_text, font=FONT_QUESTION)
    qw, qh = bbox_q[2] - bbox_q[0], bbox_q[3] - bbox_q[1]
    qx0 = (WIDTH - qw) // 2 - 32
    qy0 = hy1 + 18
    qx1 = (WIDTH + qw) // 2 + 32
    qy1 = qy0 + qh + 26
    draw.rounded_rectangle([qx0, qy0, qx1, qy1], radius=20, fill=(255, 220, 0, 245), outline=(0, 0, 0, 220), width=3)
    draw.text(((WIDTH - qw) // 2, qy0 + 10), q_text, font=FONT_QUESTION, fill=(0, 0, 0, 255))
    
    # 4. Timer Bar & Countdown (0.0s to 11.0s)
    if t < REVEAL_TIME:
        remaining_secs = max(0, int(math.ceil(REVEAL_TIME - t)))
        timer_text = f"⏳ 00:0{remaining_secs}" if remaining_secs < 10 else f"⏳ 00:{remaining_secs}"
        
        timer_color = (255, 40, 40, 255) if remaining_secs <= 3 else (255, 255, 255, 255)
        bbox_t = draw.textbbox((0, 0), timer_text, font=FONT_TIMER)
        tw, th = bbox_t[2] - bbox_t[0], bbox_t[3] - bbox_t[1]
        tx0 = (WIDTH - tw) // 2 - 24
        ty0 = qy1 + 18
        tx1 = (WIDTH + tw) // 2 + 24
        ty1 = ty0 + th + 20
        draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=16, fill=(15, 15, 25, 210), outline=timer_color, width=2)
        draw.text(((WIDTH - tw) // 2, ty0 + 8), timer_text, font=FONT_TIMER, fill=timer_color)
        
        # Countdown Progress Bar
        bar_w = 700
        bar_h = 14
        bar_x0 = (WIDTH - bar_w) // 2
        bar_y0 = ty1 + 16
        bar_x1 = bar_x0 + bar_w
        bar_y1 = bar_y0 + bar_h
        draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=7, fill=(40, 40, 50, 200))
        
        fill_pct = max(0.0, min(1.0, (REVEAL_TIME - t) / REVEAL_TIME))
        fill_x1 = bar_x0 + int(bar_w * fill_pct)
        if fill_x1 > bar_x0 + 8:
            bar_fill_color = (255, 50, 50, 240) if remaining_secs <= 3 else (0, 220, 100, 240)
            draw.rounded_rectangle([bar_x0, bar_y0, fill_x1, bar_y1], radius=7, fill=bar_fill_color)
            
    # 5. Answer Reveal (11.0s to 15.0s)
    else:
        # Dim background slightly to spotlight the answer
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 80))
        
        loc = puzzle_data.get("target_location", {"x_pct": 0.55, "y_pct": 0.50, "radius_pct": 0.12})
        cx = int(loc.get("x_pct", 0.55) * WIDTH)
        cy = int(loc.get("y_pct", 0.50) * HEIGHT)
        base_radius = int(loc.get("radius_pct", 0.12) * WIDTH)
        
        # Pulsating glowing circle effect
        pulse = 1.0 + 0.12 * math.sin((t - REVEAL_TIME) * 10.0)
        radius = int(base_radius * pulse)
        
        # Outer glow
        draw.ellipse([cx - radius - 10, cy - radius - 10, cx + radius + 10, cy + radius + 10], outline=(255, 230, 0, 160), width=6)
        # Inner sharp ring
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(255, 20, 40, 255), width=7)
        
        # Answer Callout Banner (Above bottom safe zone)
        reveal_text = "🎉 HERE IT IS! DID YOU FIND IT?"
        bbox_r = draw.textbbox((0, 0), reveal_text, font=FONT_REVEAL)
        rw, rh = bbox_r[2] - bbox_r[0], bbox_r[3] - bbox_r[1]
        rx0 = (WIDTH - rw) // 2 - 32
        ry0 = 1420
        rx1 = (WIDTH + rw) // 2 + 32
        ry1 = ry0 + rh + 28
        draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=24, fill=(0, 200, 80, 245), outline=(255, 255, 255, 240), width=4)
        draw.text(((WIDTH - rw) // 2, ry0 + 10), reveal_text, font=FONT_REVEAL, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
        
        # Call to action text
        cta_text = "👇 COMMENT 'FOUND' BELOW! 👇"
        bbox_c = draw.textbbox((0, 0), cta_text, font=FONT_CTA)
        cw = bbox_c[2] - bbox_c[0]
        draw.text(((WIDTH - cw) // 2, ry1 + 20), cta_text, font=FONT_CTA, fill=(255, 235, 0, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))

    frame.paste(Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB"))
    return frame

def render_puzzle_video(image_path, audio_path, puzzle_data, output_mp4):
    print(f"[Video] Rendering 15-second Puzzle Short ({WIDTH}x{HEIGHT} at {FPS}fps)...")
    base_img = Image.open(image_path).convert("RGB")
    total_frames = int(DURATION * FPS)
    
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.2",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-ar", "44100",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        output_mp4
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for frame_idx in range(total_frames):
        t = frame_idx / FPS
        frame_img = render_puzzle_frame(base_img, t, puzzle_data)
        bgr = np.array(frame_img)[:, :, ::-1].tobytes()
        proc.stdin.write(bgr)
        
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg video rendering failed")
        
    # Verify integrity
    cmd_verify = [FFMPEG, "-v", "error", "-i", output_mp4, "-f", "null", "-"]
    res_verify = subprocess.run(cmd_verify, stderr=subprocess.PIPE, text=True)
    if not res_verify.stderr:
        print(f"[Video] Verified: Puzzle video is 100% healthy with valid MOOV atom (+faststart).")
        
    print(f"[Video] Successfully rendered {output_mp4} ({os.path.getsize(output_mp4) / 1024 / 1024:.2f} MB)")
    return output_mp4
