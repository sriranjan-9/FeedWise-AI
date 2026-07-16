"""
FeedWise Prototype - Thumbnail Generator
--------------------------------------------
Generates stylized, illustrated 16:9 thumbnails for every creator in the
dataset -- geometric abstract avatars with category-tinted gradients, not
photos of real people. Each creator gets one consistent thumbnail, reused
across all of their posts (same as a real platform, where a creator's
videos share their channel's visual identity).

Outputs:
  thumbnails/<creator_name>.png   -- one per unique creator
  thumbnail_map.json              -- {post_id: "creator_name.png"} for every post

Run: python3 generate_thumbnails.py
"""

import json
import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 400, 225  # 16:9

CATEGORY_PALETTES = {
    # (bg_top, bg_bottom, accent)
    "Comedy":  ((255, 214, 92),  (242, 130, 60),  (255, 255, 255)),
    "Gaming":  ((104, 62, 214),  (32, 18, 74),    (110, 231, 192)),
    "News":    ((70, 90, 120),   (25, 32, 48),    (240, 240, 240)),
    "Sports":  ((255, 122, 89),  (170, 40, 60),   (255, 255, 255)),
    "Cooking": ((255, 176, 84),  (196, 96, 40),   (255, 245, 220)),
    "Fitness": ((255, 92, 122),  (140, 30, 70),   (255, 255, 255)),
    "Music":   ((190, 90, 220),  (70, 20, 110),   (255, 235, 120)),
    "Fashion": ((255, 150, 190), (150, 40, 100),  (255, 255, 255)),
    "Tech":    ((90, 200, 220),  (20, 70, 110),   (240, 250, 255)),
    "Travel":  ((110, 210, 190), (20, 90, 100),   (255, 250, 235)),
    "Academics": ((90, 140, 235), (25, 40, 100),  (255, 232, 130)),
    "Arts":      ((235, 140, 190), (110, 40, 130), (255, 255, 255)),
    "Edits":     ((40, 40, 55),   (10, 10, 18),   (255, 60, 100)),
    "Cars":      ((60, 70, 85),   (15, 18, 24),   (255, 190, 40)),
    "Anime":     ((255, 90, 140), (120, 20, 90),  (255, 255, 255)),
    "Pets":      ((255, 190, 110),(220, 130, 60), (255, 255, 255)),
    "Finance":   ((90, 200, 140), (20, 90, 60),   (255, 232, 130)),
    "DIY":       ((110, 200, 200),(30, 100, 100),  (255, 255, 255)),
    "Trending":  ((255, 80, 150), (150, 20, 100), (255, 232, 90)),
    "Science":   ((100, 180, 255),(20, 50, 120),  (180, 255, 240)),
    "History":   ((200, 170, 110),(90, 65, 30),   (255, 240, 200)),
    "BookTok":   ((180, 130, 230),(80, 40, 120),  (255, 255, 255)),
    "Motivation":((255, 160, 70), (170, 70, 20),  (255, 245, 220)),
    "Photography":((130, 140, 160),(30, 35, 50),  (255, 255, 255)),
    "FoodReviews":((255, 130, 100),(160, 50, 40), (255, 245, 220)),
}

CREATOR_CATEGORY = {}  # filled from dataset


def seeded_rng(name):
    """Deterministic pseudo-random values derived from the creator's name,
    so the same creator always gets the same look."""
    h = hashlib.sha256(name.encode()).hexdigest()
    return [int(h[i:i+4], 16) for i in range(0, 32, 4)]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_gradient(draw, palette):
    top, bottom, _ = palette
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=lerp(top, bottom, t))


def draw_avatar(img, draw, name, palette):
    seed = seeded_rng(name)
    _, _, accent = palette

    cx, cy = W // 2, H // 2 - 10
    head_r = 46

    # soft glow behind head
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx-head_r-22, cy-head_r-22, cx+head_r+22, cy+head_r+22],
                  fill=(255, 255, 255, 35))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)

    # head shape -- alternate between circle / rounded-square / hexagon based on seed
    shape_type = seed[0] % 3
    head_fill = (255, 255, 255, 235)
    head_color = (255, 250, 245)

    if shape_type == 0:
        draw.ellipse([cx-head_r, cy-head_r, cx+head_r, cy+head_r], fill=head_color)
    elif shape_type == 1:
        draw.rounded_rectangle([cx-head_r, cy-head_r, cx+head_r, cy+head_r],
                                radius=20, fill=head_color)
    else:
        pts = []
        for i in range(6):
            angle = math.pi/3 * i - math.pi/2
            pts.append((cx + head_r*math.cos(angle), cy + head_r*math.sin(angle)))
        draw.polygon(pts, fill=head_color)

    # eyes -- simple, varied spacing/shape based on seed
    eye_w = 8 + (seed[1] % 6)
    eye_gap = 22 + (seed[2] % 10)
    eye_y = cy - 4
    eye_shape = seed[3] % 2
    dark = (35, 30, 45)
    for dx in (-eye_gap, eye_gap):
        ex = cx + dx
        if eye_shape == 0:
            draw.ellipse([ex-eye_w/2, eye_y-eye_w/2, ex+eye_w/2, eye_y+eye_w/2], fill=dark)
        else:
            draw.rounded_rectangle([ex-eye_w/2, eye_y-eye_w/3, ex+eye_w/2, eye_y+eye_w/3],
                                    radius=3, fill=dark)

    # mouth -- arc, varied curve
    mouth_w = 26 + (seed[4] % 14)
    mouth_y = cy + 16
    curve = 6 + (seed[5] % 10)
    draw.arc([cx-mouth_w/2, mouth_y-curve, cx+mouth_w/2, mouth_y+curve*2],
              start=20, end=160, fill=dark, width=4)

    # accessory accent shape (varies per creator) -- small geometric mark
    accessory = seed[6] % 4
    if accessory == 0:
        draw.ellipse([cx+head_r-14, cy-head_r+2, cx+head_r+10, cy-head_r+26], fill=accent)
    elif accessory == 1:
        draw.rectangle([cx-8, cy-head_r-14, cx+8, cy-head_r+2], fill=accent)
    elif accessory == 2:
        draw.polygon([(cx-head_r+4, cy-head_r+10), (cx-head_r+24, cy-head_r+2),
                      (cx-head_r+24, cy-head_r+22)], fill=accent)
    # accessory 3: none, keep it clean


def draw_banner(draw, category, name, palette):
    _, _, accent = palette
    band_h = 46
    draw.rectangle([0, H-band_h, W, H], fill=(15, 12, 25, 235))
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font_bold = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.ellipse([14, H-band_h+13, 14+20, H-band_h+13+20], fill=accent)
    draw.text((44, H-band_h+8), name, font=font_bold, fill=(245, 240, 255))
    draw.text((44, H-band_h+26), category, font=font_small, fill=(180, 170, 210))


def generate_thumbnail(name, category, out_path):
    palette = CATEGORY_PALETTES.get(category, CATEGORY_PALETTES["Tech"])
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, palette)
    draw_avatar(img, draw, name, palette)
    draw = ImageDraw.Draw(img)
    draw_banner(draw, category, name, palette)
    img.save(out_path, "PNG")


def main():
    with open("dataset.json") as f:
        posts = json.load(f)

    for p in posts:
        CREATOR_CATEGORY[p["creator"]] = p["category"]

    os.makedirs("thumbnails", exist_ok=True)

    for creator, category in CREATOR_CATEGORY.items():
        out_path = os.path.join("thumbnails", f"{creator}.png")
        generate_thumbnail(creator, category, out_path)
        print(f"generated {out_path} ({category})")

    thumbnail_map = {p["id"]: f"{p['creator']}.png" for p in posts}
    with open("thumbnail_map.json", "w") as f:
        json.dump(thumbnail_map, f, indent=2)

    print(f"\nDone. {len(CREATOR_CATEGORY)} unique creator thumbnails generated.")
    print("thumbnail_map.json maps every post_id -> its creator's thumbnail file.")


if __name__ == "__main__":
    main()
