import os
import logging
import numpy as np

logger = logging.getLogger(__name__)


def generate_voiceover(script: str, voice: str, rate: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    try:
        from kokoro import KPipeline
        import soundfile as sf
        logger.info("Using Kokoro TTS...")
        pipeline = KPipeline(lang_code='a')
        kokoro_voice = {"en-US-GuyNeural": "am_adam", "en-US-ChristopherNeural": "am_michael",
                        "en-US-EricNeural": "am_echo", "en-US-BrianNeural": "am_liam"}.get(voice, "am_adam")
        chunks = []
        for _, _, audio in pipeline(script, voice=kokoro_voice, speed=1.2):
            chunks.append(audio)
        if chunks:
            sf.write(output_path, np.concatenate(chunks), 24000)
            logger.info(f"Kokoro voiceover saved: {output_path}")
            return output_path
    except Exception as e:
        logger.warning(f"Kokoro failed: {e} — using gTTS")

    from gtts import gTTS
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(output_path)
    logger.info(f"gTTS voiceover saved: {output_path}")
    return output_path
