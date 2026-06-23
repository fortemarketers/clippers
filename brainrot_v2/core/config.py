import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UPLOAD_ENABLED = os.getenv("UPLOAD_ENABLED", "false").lower() == "true"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKGROUNDS_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "assets", "audio_cache")
OUTPUT_VIDEOS_DIR = os.path.join(BASE_DIR, "output", "videos")
OUTPUT_THUMBS_DIR = os.path.join(BASE_DIR, "output", "thumbnails")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")

for d in [BACKGROUNDS_DIR, AUDIO_CACHE_DIR, OUTPUT_VIDEOS_DIR,
          OUTPUT_THUMBS_DIR, LOGS_DIR, CREDENTIALS_DIR]:
    os.makedirs(d, exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MAX_DURATION = 57
