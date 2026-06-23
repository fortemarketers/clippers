import os
import requests
import logging
from core.config import PEXELS_API_KEY, BACKGROUNDS_DIR

logger = logging.getLogger(__name__)

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

TOPIC_KEYWORDS = {
    "science": ["space galaxy", "dna molecule", "laboratory", "universe stars", "physics"],
    "history": ["ancient ruins", "historical architecture", "medieval", "ancient egypt", "civilization"],
    "finance": ["money cash", "stock market", "city skyline", "gold coins", "business"],
    "psychology": ["brain neurons", "human mind", "meditation", "neural network", "psychology"],
    "technology": ["technology digital", "circuit board", "artificial intelligence", "cyber network", "data"],
    "default": ["satisfying", "abstract motion", "colorful", "cinematic", "aerial city"],
}


def get_keywords_for_niche(niche: str) -> list:
    for key in TOPIC_KEYWORDS:
        if key in niche.lower():
            return TOPIC_KEYWORDS[key]
    return TOPIC_KEYWORDS["default"]


def download_from_pexels(query: str, count: int = 3) -> list:
    downloaded = []
    try:
        url = f"https://api.pexels.com/videos/search?query={query}&per_page={count}&orientation=portrait&size=medium"
        headers = {"Authorization": PEXELS_API_KEY}
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()
        for video in data.get("videos", []):
            files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
            if not files:
                continue
            best = sorted(files, key=lambda x: x.get("width", 0))[0]
            link = best.get("link")
            if not link:
                continue
            fname = os.path.join(BACKGROUNDS_DIR, f"bg_{video['id']}.mp4")
            if os.path.exists(fname):
                downloaded.append(fname)
                continue
            r = requests.get(link, timeout=60, stream=True)
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded.append(fname)
            logger.info(f"Downloaded: {fname}")
    except Exception as e:
        logger.error(f"Pexels error for '{query}': {e}")
    return downloaded


def download_from_pixabay(query: str, count: int = 3) -> list:
    if not PIXABAY_API_KEY:
        return []
    downloaded = []
    try:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}&per_page={count}&video_type=film&orientation=vertical"
        res = requests.get(url, timeout=15)
        data = res.json()
        for video in data.get("hits", []):
            videos = video.get("videos", {})
            medium = videos.get("medium", {}) or videos.get("small", {})
            link = medium.get("url")
            if not link:
                continue
            fname = os.path.join(BACKGROUNDS_DIR, f"bg_pixabay_{video['id']}.mp4")
            if os.path.exists(fname):
                downloaded.append(fname)
                continue
            r = requests.get(link, timeout=60, stream=True)
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded.append(fname)
            logger.info(f"Downloaded Pixabay: {fname}")
    except Exception as e:
        logger.error(f"Pixabay error for '{query}': {e}")
    return downloaded


def download_backgrounds(niche: str = "default", min_count: int = 10):
    os.makedirs(BACKGROUNDS_DIR, exist_ok=True)
    existing = [f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith('.mp4')]
    if len(existing) >= min_count:
        logger.info(f"Backgrounds exist: {len(existing)} files")
        return
    keywords = get_keywords_for_niche(niche)
    logger.info(f"Downloading {niche} backgrounds...")
    for keyword in keywords:
        download_from_pexels(keyword, count=3)
        download_from_pixabay(keyword, count=2)
    total = len([f for f in os.listdir(BACKGROUNDS_DIR) if f.endswith('.mp4')])
    logger.info(f"Total backgrounds: {total}")


def get_niche_backgrounds(niche: str) -> list:
    all_files = [
        os.path.join(BACKGROUNDS_DIR, f)
        for f in os.listdir(BACKGROUNDS_DIR)
        if f.endswith('.mp4')
    ]
    return all_files
