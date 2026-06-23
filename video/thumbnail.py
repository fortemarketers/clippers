import os
import logging
from PIL import Image, ImageDraw, ImageFont
from core.config import OUTPUT_THUMBS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT

logger = logging.getLogger(__name__)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def generate_thumbnail(title: str, accent: str, bg: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), hex_to_rgb(bg))
    draw = ImageDraw.Draw(img)
    accent_rgb = hex_to_rgb(accent)

    draw.rectangle([(0, 0), (VIDEO_WIDTH, 14)], fill=accent_rgb)
    draw.rectangle([(0, VIDEO_HEIGHT-14), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=accent_rgb)

    try:
        font_big = ImageFont.truetype(FONT_PATH, 100)
        font_small = ImageFont.truetype(FONT_PATH, 48)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = font_big

    words = title.upper().split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= 15:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = VIDEO_HEIGHT // 2 - (len(lines) * 110) // 2
    for line in lines[:4]:
        draw.text((VIDEO_WIDTH//2 + 3, y + 3), line, font=font_big, fill=(0,0,0), anchor="mm")
        draw.text((VIDEO_WIDTH//2, y), line, font=font_big, fill=(255,255,255), anchor="mm")
        y += 115

    badge = "WATCH TILL END 👀"
    draw.rectangle([(80, VIDEO_HEIGHT-200), (VIDEO_WIDTH-80, VIDEO_HEIGHT-130)], fill=accent_rgb)
    draw.text((VIDEO_WIDTH//2, VIDEO_HEIGHT-165), badge, font=font_small, fill=(0,0,0), anchor="mm")

    img.save(output_path, "JPEG", quality=95)
    logger.info(f"Thumbnail saved: {output_path}")
    return output_path
