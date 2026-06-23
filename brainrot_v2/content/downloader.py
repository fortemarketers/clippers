import os
import requests
import logging
from core.config import PEXELS_API_KEY, BACKGROUNDS_DIR

logger = logging.getLogger(__name__)

QUERIES = ["satisfying", "nature aerial", "city timelapse", "abstract motion",
           "ocean waves", "forest", "rain", "night city", "stars timelapse", "fire"]

def download_backgrounds(min_count=20):
    existing = [f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith('.mp4')]
    if len(existing) >= min_count:
        logger.info(f"Backgrounds already downloaded: {len(existing)} files")
        return

    logger.info("Downloading background videos from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    downloaded = 0

    for query in QUERIES:
        try:
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait&size=medium"
            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()

            for video in data.get("videos", []):
                files = video.get("video_files", [])
                mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
                if not mp4_files:
                    continue

                best = sorted(mp4_files, key=lambda x: x.get("width", 0))[0]
                link = best.get("link")
                if not link:
                    continue

                fname = os.path.join(BACKGROUNDS_DIR, f"bg_{video['id']}.mp4")
                if os.path.exists(fname):
                    continue

                r = requests.get(link, timeout=60, stream=True)
                with open(fname, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                downloaded += 1
                logger.info(f"Downloaded: bg_{video['id']}.mp4")

        except Exception as e:
            logger.error(f"Pexels download error for '{query}': {e}")

    logger.info(f"Total backgrounds downloaded: {downloaded}")
