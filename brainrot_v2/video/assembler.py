import os
import random
import logging
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip,
    CompositeVideoClip, ColorClip, concatenate_videoclips
)
from core.config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    BACKGROUNDS_DIR, OUTPUT_VIDEOS_DIR
)

logger = logging.getLogger(__name__)


def get_background(duration: float):
    files = [f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith('.mp4')]
    if files:
        path = os.path.join(BACKGROUNDS_DIR, random.choice(files))
        clip = VideoFileClip(path).resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        if clip.duration < duration:
            loops = int(duration / clip.duration) + 1
            clip = concatenate_videoclips([clip] * loops)
        return clip.subclip(0, duration).without_audio()
    else:
        return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(10, 10, 20), duration=duration)


def make_subtitles(script: str, duration: float):
    words = script.split()
    chunk_size = 5
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    time_per = duration / max(len(chunks), 1)
    clips = []

    for i, chunk in enumerate(chunks):
        text = " ".join(chunk)
        start = i * time_per
        end = min(start + time_per, duration)
        try:
            tc = (TextClip(text, fontsize=68, font="DejaVu-Sans-Bold",
                           color="white", stroke_color="black", stroke_width=3,
                           method="caption", size=(VIDEO_WIDTH - 80, None), align="center")
                  .set_start(start).set_end(end)
                  .set_position(("center", int(VIDEO_HEIGHT * 0.52))))
            clips.append(tc)
        except Exception as e:
            logger.warning(f"Subtitle clip error: {e}")
    return clips


def assemble_video(script: str, audio_path: str, watermark: str,
                   output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    audio = AudioFileClip(audio_path)
    duration = min(audio.duration + 0.3, 57.0)
    bg = get_background(duration)
    subtitles = make_subtitles(script, audio.duration)

    hook = " ".join(script.split()[:4]).upper()
    layers = [bg]

    try:
        hook_clip = (TextClip(hook, fontsize=58, font="DejaVu-Sans-Bold",
                              color="#FFD700", stroke_color="black", stroke_width=3,
                              method="caption", size=(VIDEO_WIDTH - 100, None), align="center")
                     .set_duration(2.5).set_position(("center", 200)))
        layers.append(hook_clip)
    except Exception:
        pass

    layers += subtitles

    try:
        wm = (TextClip(watermark, fontsize=30, font="DejaVu-Sans",
                       color="white", stroke_color="black", stroke_width=1)
              .set_duration(duration).set_position((40, VIDEO_HEIGHT - 90)).set_opacity(0.75))
        layers.append(wm)
    except Exception:
        pass

    final = CompositeVideoClip(layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    final = final.set_audio(audio).set_duration(duration)
    final.write_videofile(output_path, fps=VIDEO_FPS, codec="libx264",
                          audio_codec="aac", preset="fast", threads=4, logger=None)
    logger.info(f"Video assembled: {output_path}")
    return output_path
