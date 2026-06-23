import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def generate_voiceover(script: str, voice: str, rate: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    # Try piper-tts (lightweight, good quality)
    try:
        import urllib.request
        model_path = "/tmp/piper_en_us.onnx"
        config_path = "/tmp/piper_en_us.onnx.json"
        if not os.path.exists(model_path):
            logger.info("Downloading Piper model...")
            urllib.request.urlretrieve(
                "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx",
                model_path
            )
            urllib.request.urlretrieve(
                "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json",
                config_path
            )
        wav_path = output_path.replace('.mp3', '.wav')
        result = subprocess.run(
            ['piper', '--model', model_path, '--output_file', wav_path],
            input=script.encode(),
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0 and os.path.exists(wav_path):
            subprocess.run(['ffmpeg', '-i', wav_path, '-codec:a', 'libmp3lame',
                          '-qscale:a', '2', output_path, '-y'],
                         capture_output=True)
            os.remove(wav_path)
            logger.info(f"Piper voiceover saved: {output_path}")
            return output_path
    except Exception as e:
        logger.warning(f"Piper failed: {e} — using gTTS")

    from gtts import gTTS
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(output_path)
    logger.info(f"gTTS voiceover saved: {output_path}")
    return output_path
