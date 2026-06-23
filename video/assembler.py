import os
import random
import logging
from moviepy.editor import (
    VideoFileClip, AudioFileClip,
    CompositeVideoClip, ColorClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.video.VideoClip import ImageClip
from core.config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, BACKGROUNDS_DIR

logger = logging.getLogger(__name__)


def make_text_image(text, width, fontsize=68, color=(255,255,255),
                    stroke_color=(0,0,0), stroke_width=3):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fontsize)
    except Exception:
        font = ImageFont.load_default()
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = stroke_width + 10
    img = Image.new("RGBA", (min(tw + pad*2, width), th + pad*2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x, y = pad, pad
    for dx in range(-stroke_width, stroke_width+1):
        for dy in range(-stroke_width, stroke_width+1):
            draw.text((x+dx, y+dy), text, font=font, fill=stroke_color+(255,))
    draw.text((x, y), text, font=font, fill=color+(255,))
    return np.array(img)


def get_background(duration: float):
    files = [f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith('.mp4')]
    if files:
        path = os.path.join(BACKGROUNDS_DIR, random.choice(files))
        clip = VideoFileClip(path).resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        if clip.duration < duration:
            loops = int(duration / clip.duration) + 1
            clip = concatenate_videoclips([clip] * loops)
        return clip.subclip(0, duration).without_audio()
    return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(10, 10, 20), duration=duration)


def make_subtitle_clips(script: str, duration: float):
    words = script.split()
    chunks = [words[i:i+5] for i in range(0, len(words), 5)]
    time_per = duration / max(len(chunks), 1)
    clips = []
    for i, chunk in enumerate(chunks):
        text = " ".join(chunk)
        start = i * time_per
        end = min(start + time_per, duration - 0.1)
        try:
            arr = make_text_image(text, VIDEO_WIDTH - 80)
            clip = (ImageClip(arr, ismask=False)
                    .set_start(start).set_end(end)
                    .set_position(("center", int(VIDEO_HEIGHT * 0.52))))
            clips.append(clip)
        except Exception as e:
            logger.warning(f"Subtitle error: {e}")
    return clips


def assemble_video(script: str, audio_path: str, watermark: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    audio = AudioFileClip(audio_path)
    duration = min(audio.duration, 57.0)
    audio = audio.subclip(0, duration)
    bg = get_background(duration)
    layers = [bg] + make_subtitle_clips(script, duration)
    try:
        hook_arr = make_text_image(" ".join(script.split()[:4]).upper(),
                                   VIDEO_WIDTH - 100, fontsize=58, color=(255, 215, 0))
        layers.append(ImageClip(hook_arr).set_duration(min(2.5, duration)).set_position(("center", 200)))
    except Exception as e:
        logger.warning(f"Hook error: {e}")
    try:
        wm_arr = make_text_image(watermark, 400, fontsize=30, stroke_width=2)
        layers.append(ImageClip(wm_arr).set_duration(duration).set_position((40, VIDEO_HEIGHT - 90)).set_opacity(0.8))
    except Exception as e:
        logger.warning(f"Watermark error: {e}")
    final = CompositeVideoClip(layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    final = final.set_audio(audio).set_duration(duration)
    final.write_videofile(output_path, fps=VIDEO_FPS, codec="libx264",
                          audio_codec="aac", preset="fast", threads=4, logger=None)
    logger.info(f"Video assembled: {output_path}")
    return output_path
