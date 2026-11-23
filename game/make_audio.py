# Audio for the Star Catcher video: a simple chiptune loop (sine melody +
# bass, 140 BPM) with a bright blip on every star catch. Catch times are
# re-derived from the same deterministic simulation as game/render.py
# (seed 7, same spawn schedule and basket path), so blips land exactly on
# the catches you see. Written from scratch in this session.
import math, random, struct, sys, wave

SR = 44100
DUR = 24.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "audio.wav"

# --- same simulation as render.py (seed 7) -------------------------------
rng = random.Random(7)
stars = []
t = 0.2
i = 0
while t < 19.0:
    stars.append((t, rng.uniform(90, 990)))
    t += 0.45
    i += 1

def basket_x(tt):
    return 540 + 380 * math.sin(2 * math.pi * tt / 6.0 + 0.6)

catch_times = []
for (spawn, x) in stars:
    tc = spawn + (1640 + 20 + 40) / 430.0
    if abs(x - basket_x(tc)) <= 140:
        catch_times.append(tc)

# --- notes ----------------------------------------------------------------
# C major pentatonic, 8th notes at 140 BPM (0.2142857 s each)
N = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00,
     "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99, "A5": 880.00,
     "C3": 130.81, "A2": 110.00, "F2": 87.31, "G2": 98.00}
BARS = [
    (["C5", "E5", "G5", "E5", "A5", "G5", "E5", "D5"], "C3"),
    (["E5", "G5", "A5", "G5", "E5", "C5", "D5", "E5"], "A2"),
    (["G5", "A5", "G5", "E5", "C5", "E5", "G5", "A5"], "F2"),
    (["A5", "G5", "E5", "D5", "E5", "G5", "E5", "C5"], "G2"),
]
EIGHTH = 60.0 / 140.0 / 2.0

n = int(SR * DUR)
buf = [0.0] * n

def add_note(t0, dur, freq, amp, bright=False):
    s0 = int(t0 * SR)
    s1 = min(n, int((t0 + dur) * SR))
    for s in range(s0, s1):
        tt = (s - s0) / SR
        env = min(1.0, tt / 0.012) * math.exp(-2.2 * tt / dur)
        v = math.sin(2 * math.pi * freq * tt)
        if bright:
            v += 0.35 * math.sin(2 * math.pi * freq * 2 * tt)
        buf[s] += amp * env * v

bar_len = 8 * EIGHTH
bar = 0
while bar * bar_len < DUR:
    mel, bass = BARS[bar % len(BARS)]
    for k, name in enumerate(mel):
        add_note(bar * bar_len + k * EIGHTH, EIGHTH * 0.95, N[name], 0.30, bright=True)
    add_note(bar * bar_len, bar_len, N[bass], 0.16)
    add_note(bar * bar_len, bar_len, N[bass] * 1.5, 0.07)
    bar += 1

for ct in catch_times:
    if ct < DUR:
        add_note(ct, 0.10, 1318.5, 0.35, bright=True)

peak = max(abs(v) for v in buf) or 1.0
gain = 0.89 / peak
w = wave.open(OUT, "wb")
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(SR)
frames = bytearray()
for v in buf:
    s = max(-32767, min(32767, int(v * gain * 32767)))
    frames += struct.pack("<hh", s, s)
w.writeframes(bytes(frames))
w.close()
print("audio written", OUT, "catch blips:", len([c for c in catch_times if c < DUR]))
