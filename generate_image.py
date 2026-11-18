"""Render entry.png: a one-page newspaper front page summing up the world
news of Tuesday 17 November 2026, from stories.json. Run: python3 generate_image.py
Writes entry.png (1024x1024) next to this script."""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

PAPER = (251, 247, 239)   # warm off-white paper
INK = (26, 26, 26)        # near-black text
MUTED = (90, 86, 78)      # grey-brown secondary text
RED = (176, 30, 36)       # masthead accent
RULE = (26, 26, 26)
HAIRLINE = (190, 182, 168)

TAG_COLORS = {
    "MIDDLE EAST · WAR": (140, 47, 57),
    "EUROPE · WAR": (31, 78, 121),
    "ASIA · DIPLOMACY": (46, 107, 52),
    "ASIA · SECURITY": (120, 72, 20),
    "MIDDLE EAST · AID": (140, 47, 57),
    "EUROPE · JUSTICE": (90, 60, 120),
    "UNITED STATES": (60, 60, 60),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, name, start_size, max_width):
    """Largest font size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > 10:
        fnt = font(name, size)
        if draw.textlength(text, font=fnt) <= max_width:
            return fnt
        size -= 1
    return font(name, 10)


def draw_tag(draw, x, y, tag):
    fnt = font("DejaVuSans-Bold.ttf", 17)
    tw = draw.textlength(tag, font=fnt)
    pad_x, pad_y = 10, 5
    color = TAG_COLORS.get(tag, (60, 60, 60))
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + 27],
                           radius=4, fill=color)
    draw.text((x + pad_x, y + pad_y), tag, font=fnt, fill=(255, 255, 255))
    return tw + 2 * pad_x


def draw_story(draw, x, y, w, story, headline_size, summary_size, max_head_lines=2):
    tag = story["tag"]
    draw_tag(draw, x, y, tag)
    y += 27 + 9
    hf = font("DejaVuSans-Bold.ttf", headline_size)
    lines = wrap(draw, story["headline"], hf, w)[:max_head_lines]
    for line in lines:
        draw.text((x, y), line, font=hf, fill=INK)
        y += headline_size + 6
    y += 2
    sf = font("DejaVuSans.ttf", summary_size)
    lines = wrap(draw, story["summary"], sf, w)
    for line in lines:
        draw.text((x, y), line, font=sf, fill=(52, 48, 44))
        y += summary_size + 7
    return y


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
        data = json.load(f)
    stories = data["stories"]

    W = H = 1024
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 40  # margin
    x0, x1 = M, W - M

    # ---- Masthead ----
    y = 24
    mast = font("DejaVuSerif-Bold.ttf", 42)
    title = "THE WORLD IN A DAY"
    tw = d.textlength(title, font=mast)
    d.text(((W - tw) / 2, y), title, font=mast, fill=INK)
    y += 52
    d.line([(x0, y), (x1, y)], fill=RULE, width=3)
    y += 10

    # ---- Big date (auto-fit so it never clips) ----
    date = "TUESDAY 17 NOVEMBER 2026"
    date_f = fit_font(d, date, "DejaVuSans-Bold.ttf", 56, x1 - x0)
    tw = d.textlength(date, font=date_f)
    d.text(((W - tw) / 2, y), date, font=date_f, fill=RED)
    y += date_f.size + 14
    sub_f = font("DejaVuSans.ttf", 21)
    sub = "Seven stories that defined the day — in one image"
    tw = d.textlength(sub, font=sub_f)
    d.text(((W - tw) / 2, y), sub, font=sub_f, fill=MUTED)
    y += 30
    d.line([(x0, y), (x1, y)], fill=RULE, width=3)
    y += 5
    d.line([(x0, y), (x1, y)], fill=HAIRLINE, width=1)
    y += 16

    # ---- Lead story (full width) ----
    y = draw_story(d, x0, y, x1 - x0, stories[0],
                   headline_size=32, summary_size=21, max_head_lines=2)
    y += 4
    d.line([(x0, y), (x1, y)], fill=HAIRLINE, width=1)
    y += 14

    # ---- Remaining six stories: 2 columns x 3 rows ----
    col_w = (x1 - x0 - 28) // 2
    row_h = 183
    for i, story in enumerate(stories[1:]):
        col = i % 2
        row = i // 2
        sx = x0 + col * (col_w + 28)
        sy = y + row * row_h
        if col == 1:
            d.line([(x0 + col_w + 14, sy - 4),
                    (x0 + col_w + 14, sy + row_h - 16)],
                   fill=HAIRLINE, width=1)
        draw_story(d, sx, sy, col_w, story,
                   headline_size=23, summary_size=18, max_head_lines=2)

    # ---- Footer ----
    fy = H - 34
    d.line([(x0, fy - 12), (x1, fy - 12)], fill=HAIRLINE, width=1)
    foot_f = font("DejaVuSans.ttf", 16)
    foot = "All stories as reported on 17 November 2026  ·  Sources: CNN, Reuters, Just Security, Zark News, FeedCast, Asas Press"
    tw = d.textlength(foot, font=foot_f)
    d.text(((W - tw) / 2, fy), foot, font=foot_f, fill=MUTED)

    # ---- Subtle paper grain (adds texture and file weight) ----
    grain = Image.effect_noise((W, H), 14).convert("RGB")
    img = Image.blend(img, grain, 0.02)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
