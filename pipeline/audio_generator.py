import os
import wave
import numpy as np

def generate_puzzle_audio(output_path, duration=15.0):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    audio = np.zeros_like(t)
    
    # 1. Catchy Playful Puzzle BGM (Marimba / Pluck melody in C Major)
    notes = [261.63, 329.63, 392.00, 523.25, 440.00, 392.00, 349.23, 329.63] # C4, E4, G4, C5, A4, G4, F4, E4
    melody_step = 0.5 # 120 bpm eighth notes
    for i in range(int(duration / melody_step)):
        nt = i * melody_step
        if nt < 11.0: # Play playful melody during puzzle
            freq = notes[i % len(notes)]
            dur_p = 0.35
            tp = np.linspace(0, dur_p, int(sr * dur_p), endpoint=False)
            pluck = (np.sin(2 * np.pi * freq * tp) + 0.3 * np.sin(2 * np.pi * freq * 2 * tp)) * np.exp(-tp * 10.0)
            s_idx = int(nt * sr)
            e_idx = min(s_idx + len(pluck), len(audio))
            audio[s_idx:e_idx] += pluck[:e_idx - s_idx] * 0.22
            
    # 2. Suspenseful Clock Ticking Sound on every second (from second 1 to 10)
    for sec in range(1, 11):
        t_tick = np.linspace(0, 0.08, int(sr * 0.08), endpoint=False)
        # Alternate tick (higher pitch) and tock (lower pitch)
        tick_freq = 1800 if sec % 2 == 1 else 1200
        tick = np.sin(2 * np.pi * tick_freq * t_tick) * np.exp(-t_tick * 60.0)
        s_idx = int(sec * sr)
        e_idx = min(s_idx + len(tick), len(audio))
        audio[s_idx:e_idx] += tick[:e_idx - s_idx] * 0.45
        
    # 3. Big Celebratory "Ding / Bell Chime" at second 11.0 (Answer Reveal!)
    t_ding = np.linspace(0, 3.5, int(sr * 3.5), endpoint=False)
    # Resonant metallic bell chords (C6 + E6 + G6)
    bell = (
        np.sin(2 * np.pi * 1046.50 * t_ding) * np.exp(-t_ding * 2.5) +
        0.8 * np.sin(2 * np.pi * 1318.51 * t_ding) * np.exp(-t_ding * 2.8) +
        0.6 * np.sin(2 * np.pi * 1567.98 * t_ding) * np.exp(-t_ding * 3.0) +
        0.4 * np.sin(2 * np.pi * 2093.00 * t_ding) * np.exp(-t_ding * 4.0)
    )
    s_ding = int(11.0 * sr)
    e_ding = min(s_ding + len(bell), len(audio))
    audio[s_ding:e_ding] += bell[:e_ding - s_ding] * 0.55
    
    # 4. Cheerful Outro Chords (seconds 11.5 to 15.0)
    outro_chords = [523.25, 659.25, 783.99, 1046.50]
    for k, freq in enumerate(outro_chords):
        t_ch = np.linspace(0, 3.0, int(sr * 3.0), endpoint=False)
        chord_tone = np.sin(2 * np.pi * freq * t_ch) * np.exp(-t_ch * 1.5)
        s_ch = int((11.5 + k * 0.15) * sr)
        e_ch = min(s_ch + len(chord_tone), len(audio))
        audio[s_ch:e_ch] += chord_tone[:e_ch - s_ch] * 0.20
        
    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.85
        
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
        
    print(f"[Audio] Created pure suspenseful BGM + Ticking + Chime sound track ({duration}s, zero voices): {output_path}")
    return output_path
