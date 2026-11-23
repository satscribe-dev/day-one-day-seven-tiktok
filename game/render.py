# STAR CATCHER — a tiny agent-built game, rendered as video frames.
# One deterministic simulation (seed 7) drives BOTH versions, so the
# "identical moment" cuts are truly identical: same star spawns, same
# basket path, same catches, same score. Only the presentation differs.
#   v1 DAY ONE  : flat sky, white circle stars, grey rectangle basket.
#   v2 DAY SEVEN: sunset gradient, twinkling stars, clouds, moon, hills,
#                 coloured glowing stars, catch particles, +1 popups,
#                 rocket basket with flame + trail, hearts, DAY 7 badge.
# Written from scratch in this session (23 Nov 2026) for the make.fun
# bounty "Day one, day seven" (post-tiktok-day-one-day-seven-20261123-0327).
import math, random, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
GROUND_Y = 1700
BASKET_Y = 1640
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "frames"
os.makedirs(OUT, exist_ok=True)

def font(sz):
    return ImageFont.truetype(FONT_B, sz)

def font_r(sz):
    return ImageFont.truetype(FONT_R, sz)

def text_center(d, cx, y, s, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)

# ---------------------------------------------------------------- simulation
rng = random.Random(7)
SPAWN_EVERY = 0.45
FALL_SPEED = 430.0
stars = []  # dicts: spawn, x, kind, caught, catch_t, catch_x
t = 0.2
i = 0
while t < 19.0:
    stars.append({"spawn": t, "x": rng.uniform(90, 990),
                  "kind": ["gold", "pink", "cyan"][i % 3]})
    t += SPAWN_EVERY
    i += 1

def basket_x(tt):
    return 540 + 380 * math.sin(2 * math.pi * tt / 6.0 + 0.6)

catches = []  # (catch_t, x, kind)
for s in stars:
    tc = s["spawn"] + (BASKET_Y + 20 + 40) / FALL_SPEED
    s["cross_t"] = tc
    if abs(s["x"] - basket_x(tc)) <= 140:
        s["caught"] = True
        s["catch_t"] = tc
        catches.append((tc, s["x"], s["kind"]))
    else:
        s["caught"] = False
        s["catch_t"] = None

def score_at(tt):
    return sum(1 for c in catches if c[0] <= tt)

def combo_at(tt):
    n = 0
    prev = None
    for c in catches:
        if c[0] > tt:
            break
        if prev is None or c[0] - prev < 2.0:
            n += 1
        else:
            n = 1
        prev = c[0]
    return n

# v2 background stars + particles (seeded, fixed)
brng = random.Random(11)
BG_STARS = [(brng.uniform(0, W), brng.uniform(0, 1150),
             brng.uniform(1.5, 3.5), brng.uniform(0.6, 2.2),
             brng.uniform(0, 6.28)) for _ in range(80)]
CLOUDS = [(120, 230, 150), (700, 430, 190), (350, 660, 130)]
PARTS = []
for (ct, cx, kind) in catches:
    prng = random.Random(int(ct * 1000) + 5)
    for _ in range(14):
        ang = prng.uniform(0, 6.283)
        sp = prng.uniform(120, 520)
        PARTS.append({"t0": ct, "x": cx, "y": BASKET_Y,
                      "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp - 260,
                      "life": prng.uniform(0.45, 0.75),
                      "col": {"gold": (255, 217, 61), "pink": (255, 107, 193),
                              "cyan": (77, 216, 255)}[kind]})

# v2 sky gradient, precomputed once
ys = np.linspace(0, 1, H)[:, None]
stops = [(0.00, (22, 10, 46)), (0.45, (74, 29, 107)), (0.70, (168, 58, 122)),
         (0.88, (255, 126, 95)), (1.00, (254, 180, 123))]
grad = np.zeros((H, 3), dtype=np.uint8)
for j in range(len(stops) - 1):
    y0, c0 = stops[j]
    y1, c1 = stops[j + 1]
    m = (ys >= y0) & (ys <= y1)
    f = np.clip((ys - y0) / max(y1 - y0, 1e-9), 0, 1)
    for k in range(3):
        grad[:, k] = np.where(m[:, 0], (c0[k] + (c1[k] - c0[k]) * f[:, 0]).astype(np.uint8), grad[:, k])
SKY = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1), "RGB")

KIND_COL = {"gold": (255, 217, 61), "pink": (255, 107, 193), "cyan": (77, 216, 255)}

def draw_star_v1(d, x, y, r=24):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    d.ellipse([x - r // 3, y - r // 3, x + r // 3, y + r // 3], fill=(230, 230, 255))

def draw_star_v2(base, d, x, y, kind, tt, seed):
    col = KIND_COL[kind]
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    pulse = 1.0 + 0.12 * math.sin(tt * 5 + seed)
    r = int(52 * pulse)
    for rr, a in ((r, 46), (int(r * 0.66), 90), (int(r * 0.4), 150)):
        g.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (a,))
    base.alpha_composite(glow)
    d = ImageDraw.Draw(base)
    d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=col)
    d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 255, 255))
    for dx, dy in ((0, -34), (0, 34), (-34, 0), (34, 0)):
        d.line([x, y, x + dx, y + dy], fill=(255, 255, 255, 220), width=3)

def active_stars(tt):
    out = []
    for s in stars:
        if s["spawn"] <= tt:
            y = -40 + FALL_SPEED * (tt - s["spawn"])
            if s["caught"] and tt >= s["catch_t"]:
                continue
            if y > 1760:
                continue
            out.append((s, y))
    return out

# ---------------------------------------------------------------- v1 frame
def frame_v1(tt):
    img = Image.new("RGB", (W, H), (11, 16, 38))
    d = ImageDraw.Draw(img)
    for s, y in active_stars(tt):
        draw_star_v1(d, s["x"], y)
    bx = basket_x(tt)
    d.rounded_rectangle([bx - 115, BASKET_Y - 23, bx + 115, BASKET_Y + 23],
                        radius=10, fill=(150, 150, 160))
    d.line([bx - 115, BASKET_Y - 23, bx + 115, BASKET_Y - 23], fill=(200, 200, 210), width=4)
    d.text((40, 48), "SCORE: %d" % score_at(tt), font=font(64), fill=(255, 255, 255))
    d.text((W - 40 - d.textlength("DAY 1", font=font(64)), 48), "DAY 1",
           font=font(64), fill=(160, 160, 180))
    d.line([0, GROUND_Y + 40, W, GROUND_Y + 40], fill=(60, 60, 80), width=6)
    return img

# ---------------------------------------------------------------- v2 frame
def frame_v2(tt, cta=False):
    img = SKY.copy().convert("RGBA")
    d = ImageDraw.Draw(img)
    # twinkling background stars
    for (x, y, r, f, ph) in BG_STARS:
        a = int(90 + 165 * abs(math.sin(tt * f + ph)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    # moon + glow
    mx, my = 880, 250
    for rr, a in ((150, 30), (115, 60)):
        d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=(255, 244, 200, a))
    d.ellipse([mx - 88, my - 88, mx + 88, my + 88], fill=(255, 248, 220, 255))
    d.ellipse([mx - 40, my - 20, mx - 5, my + 15], fill=(235, 225, 190, 255))
    d.ellipse([mx + 20, my + 30, mx + 55, my + 60], fill=(235, 225, 190, 255))
    # clouds
    for (cx0, cy, cw) in CLOUDS:
        cx = (cx0 + tt * 14) % 1350 - 135
        for ox, oy, orr in ((-cw // 2, 10, 42), (0, -12, 55), (cw // 2, 8, 44)):
            d.ellipse([cx + ox - orr, cy + oy - orr, cx + ox + orr, cy + oy + orr],
                      fill=(255, 255, 255, 45))
    # hills
    d.pieslice([-300, 1560, 700, 2100], 180, 360, fill=(42, 16, 64, 255))
    d.pieslice([500, 1620, 1400, 2150], 180, 360, fill=(28, 10, 46, 255))
    d.rectangle([0, 1800, W, H], fill=(28, 10, 46, 255))
    # stars
    for s, y in active_stars(tt):
        draw_star_v2(img, d, s["x"], y, s["kind"], tt, s["spawn"])
    d = ImageDraw.Draw(img)
    # catch particles + popups
    for p in PARTS:
        age = tt - p["t0"]
        if 0 <= age < p["life"]:
            px = p["x"] + p["vx"] * age
            py = p["y"] + p["vy"] * age + 500 * age * age
            a = int(255 * (1 - age / p["life"]))
            d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=p["col"] + (a,))
    for (ct, cx, kind) in catches:
        age = tt - ct
        if 0 <= age < 0.8:
            a = int(255 * (1 - age / 0.8))
            text_center(d, cx, BASKET_Y - 90 - age * 70, "+1", font(72),
                        KIND_COL[kind] + (a,), stroke=2, stroke_fill=(0, 0, 0, 160))
    # basket: rocket sled with flame + trail
    bx = basket_x(tt)
    for k in range(1, 7):
        px = 540 + 380 * math.sin(2 * math.pi * (tt - k * 0.03) / 6.0 + 0.6)
        d.rounded_rectangle([px - 115, BASKET_Y - 23, px + 115, BASKET_Y + 23],
                            radius=12, fill=(255, 90, 60, int(26 * (1 - k / 7))))
    flame = 26 + 14 * math.sin(tt * 22)
    for dx in (-70, 0, 70):
        d.polygon([(bx + dx - 22, BASKET_Y + 20), (bx + dx + 22, BASKET_Y + 20),
                   (bx + dx, BASKET_Y + 20 + flame)], fill=(255, 179, 71, 230))
    d.rounded_rectangle([bx - 115, BASKET_Y - 23, bx + 115, BASKET_Y + 23],
                        radius=12, fill=(255, 90, 60, 255))
    d.rounded_rectangle([bx - 115, BASKET_Y - 23, bx + 115, BASKET_Y - 2],
                        radius=12, fill=(255, 122, 89, 255))
    d.ellipse([bx - 34, BASKET_Y - 14, bx + 34, BASKET_Y + 14], fill=(191, 239, 255, 255))
    d.ellipse([bx - 20, BASKET_Y - 8, bx + 6, BASKET_Y + 6], fill=(255, 255, 255, 255))
    # HUD
    d.text((40, 44), "♥ ♥ ♥", font=font_r(58), fill=(255, 90, 110, 255))
    sc = score_at(tt)
    text_center(d, W // 2, 40, "SCORE %d" % sc, font(72), (255, 255, 255, 255),
                stroke=3, stroke_fill=(0, 0, 0, 120))
    combo = combo_at(tt)
    if combo >= 3:
        text_center(d, W // 2, 130, "COMBO x%d" % combo, font(52),
                    (255, 217, 61, 255), stroke=3, stroke_fill=(0, 0, 0, 120))
    d.rounded_rectangle([W - 250, 48, W - 40, 118], radius=35, fill=(255, 90, 60, 255))
    text_center(d, W - 145, 58, "DAY 7", font(52), (255, 255, 255, 255))
    d.rounded_rectangle([40, 200, W - 40, 218], radius=9, fill=(255, 255, 255, 70))
    pw = 40 + (W - 80) * min(tt / 19.0, 1.0)
    if pw > 60:
        d.rounded_rectangle([40, 200, pw, 218],
                            radius=9, fill=(77, 216, 255, 220))
    if cta:
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.rectangle([0, 560, W, 900], fill=(10, 6, 30, 150))
        img.alpha_composite(band)
        d = ImageDraw.Draw(img)
        bounce = 8 * math.sin(tt * 6)
        text_center(d, W // 2, 600 + bounce, "START YOURS AT", font(84),
                    (255, 255, 255, 255), stroke=4, stroke_fill=(0, 0, 0, 160))
        text_center(d, W // 2, 710 + bounce, "MAKE.FUN", font(150),
                    (255, 217, 61, 255), stroke=5, stroke_fill=(0, 0, 0, 160))
    return img.convert("RGB")

# ---------------------------------------------------------------- title card
def frame_title(tt):
    img = Image.new("RGB", (W, H), (16, 8, 34))
    d = ImageDraw.Draw(img)
    for (x, y, r, f, ph) in BG_STARS[:40]:
        a = int(60 + 120 * abs(math.sin(tt * f + ph)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    def fade(t0, t1):
        return max(0.0, min(1.0, (tt - t0) / (t1 - t0)))
    a1, a2, a3 = fade(0.05, 0.5), fade(0.7, 1.15), fade(1.3, 1.75)
    y1 = 700 - 30 * (1 - a1)
    text_center(d, W // 2, y1, "MY AGENT BUILT", font(92),
                (255, 255, 255, int(255 * a1)), stroke=3, stroke_fill=(0, 0, 0, 120))
    text_center(d, W // 2, y1 + 110, "A TINY GAME.", font(92),
                (255, 217, 61, int(255 * a1)), stroke=3, stroke_fill=(0, 0, 0, 120))
    y2 = 1010 - 30 * (1 - a2)
    text_center(d, W // 2, y2, "THEN UPDATED IT", font(64),
                (255, 255, 255, int(255 * a2)))
    text_center(d, W // 2, y2 + 80, "EVERY DAY FOR A WEEK.", font(64),
                (255, 255, 255, int(255 * a2)))
    text_center(d, W // 2, 1250, "DAY ONE  →  DAY SEVEN", font(54),
                (77, 216, 255, int(255 * a3)))
    return img

# ---------------------------------------------------------------- split screen
def frame_split(tt):
    top = frame_v1(tt).resize((W, 940))
    bot = frame_v2(tt).resize((W, 940))
    img = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(top, (0, 0))
    img.paste(bot, (0, 980))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 940, W, 980], fill=(255, 255, 255))
    d.rounded_rectangle([36, 430, 268, 510], radius=20, fill=(0, 0, 0, 170))
    d.text((60, 444), "DAY 1", font=font(56), fill=(255, 255, 255))
    d.rounded_rectangle([36, 1410, 268, 1490], radius=20, fill=(0, 0, 0, 170))
    d.text((60, 1424), "DAY 7", font=font(56), fill=(255, 217, 61))
    d.ellipse([W // 2 - 52, 940 - 12, W // 2 + 52, 980 + 12], fill=(255, 90, 60))
    d.text((W // 2 - 26, 940), "VS", font=font(44), fill=(255, 255, 255))
    return img

# ---------------------------------------------------------------- render plan
# 0.0-2.0 title | 2.0-10.0 split (sim t 0-8) | 10.0-18.0 v2 full (sim t 8-16)
# 18.0-21.0 v2 full + CTA (sim t 16-19) | 21.0-24.0 handled by ffmpeg (end card)
plan = []
for f in range(0, 60):
    plan.append(("title", f / FPS))
for f in range(60, 300):
    plan.append(("split", (f - 60) / FPS))
for f in range(300, 540):
    plan.append(("v2", 8 + (f - 300) / FPS))
for f in range(540, 630):
    plan.append(("v2cta", 16 + (f - 540) / FPS))
# 21.0-24.0: keep rendering v2 gameplay (sim t 19-22, stars keep falling)
for f in range(630, 720):
    plan.append(("v2", 19 + (f - 630) / FPS))

for idx, (kind, tt) in enumerate(plan):
    if kind == "title":
        img = frame_title(tt)
    elif kind == "split":
        img = frame_split(tt)
    elif kind == "v2":
        img = frame_v2(tt)
    else:
        img = frame_v2(tt, cta=True)
    img.save(os.path.join(OUT, "frame_%05d.png" % idx))
    if idx % 120 == 0:
        print("frame", idx, kind, round(tt, 2), flush=True)
print("DONE", len(plan), "frames; catches:", len(catches),
      "final score:", score_at(22.0))
