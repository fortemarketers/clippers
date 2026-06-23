import os
import sys
import time
import uuid
import logging
import schedule
from concurrent.futures import ThreadPoolExecutor
from core.config import UPLOAD_ENABLED, LOGS_DIR
from core.channels import CHANNELS, PARALLEL_WORKERS
from content.downloader import download_backgrounds
from content.picker import pick_topic
from content.generator import generate_script, generate_metadata
from content.voiceover import generate_voiceover
from video.assembler import assemble_video
from video.thumbnail import generate_thumbnail
from upload.youtube_uploader import upload_video

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "pipeline.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("orchestrator")


def run_one_video(channel_id: str, video_num: int) -> bool:
    job_id = str(uuid.uuid4())[:6]
    channel = CHANNELS[channel_id]
    logger.info(f"[{channel['name']}] Video {video_num}/10 — job {job_id}")

    try:
        content = pick_topic(channel_id)
        topic = content["topic"]

        script = generate_script(topic, channel["script_style"])
        metadata = generate_metadata(script, channel["tags"])

        audio_path = f"/tmp/audio_{job_id}.mp3"
        generate_voiceover(script, channel["voice"], channel["voice_rate"], audio_path)

        video_path = os.path.join("output", "videos", f"{channel_id}_{job_id}.mp4")
        thumb_path = os.path.join("output", "thumbnails", f"{channel_id}_{job_id}.jpg")

        assemble_video(script, audio_path, channel["watermark"], video_path)
        generate_thumbnail(metadata["title"], channel["thumb_accent"],
                           channel["thumb_bg"], thumb_path)

        if UPLOAD_ENABLED:
            video_id = upload_video(
                video_path=video_path,
                thumb_path=thumb_path,
                title=metadata["title"],
                description=metadata["description"],
                tags=metadata["tags"],
                credentials_file=channel["credentials_file"],
                token_file=channel["token_file"]
            )
            logger.info(f"[{channel['name']}] ✅ https://youtube.com/shorts/{video_id}")
        else:
            logger.info(f"[{channel['name']}] ✅ Saved locally: {video_path}")

        if os.path.exists(audio_path):
            os.remove(audio_path)
        return True

    except Exception as e:
        logger.error(f"[{channel_id}] Job {job_id} failed: {e}", exc_info=True)
        return False


def run_channel_batch(channel_id: str):
    channel = CHANNELS[channel_id]
    logger.info(f"Starting batch: {channel['name']} — 10 videos")
    success = 0
    for i in range(1, 11):
        if run_one_video(channel_id, i):
            success += 1
        time.sleep(30)
    logger.info(f"[{channel['name']}] Batch done: {success}/10 successful")


def run_daily_batch():
    logger.info("=" * 50)
    logger.info("DAILY BATCH STARTING — 5 channels x 10 videos")
    logger.info("=" * 50)

    download_backgrounds(min_count=20)

    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = {executor.submit(run_channel_batch, ch_id): ch_id
                   for ch_id in CHANNELS.keys()}
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Channel batch error: {e}")

    logger.info("DAILY BATCH COMPLETE")


def run_scheduler():
    schedule.every().day.at("07:00").do(run_daily_batch)
    logger.info("Scheduler running. Daily batch at 07:00 UTC.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "schedule"
    if cmd == "once":
        channel_id = sys.argv[2] if len(sys.argv) > 2 else "ch1_science"
        run_one_video(channel_id, 1)
    elif cmd == "batch":
        run_daily_batch()
    elif cmd == "schedule":
        run_scheduler()
