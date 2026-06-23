import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def generate_voiceover(script: str, voice: str, rate: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        import asyncio
        import edge_tts
        
        async def _generate():
            communicate = edge_tts.Communicate(script, voice=voice, rate=rate)
            await communicate.save(output_path)
        
        asyncio.run(_generate())
        logger.info(f"Voiceover saved: {output_path}")
        return output_path

    except Exception as e:
        logger.warning(f"edge-tts failed: {e} — using pyttsx3 fallback")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 1.0)
            engine.save_to_file(script, output_path.replace('.mp3', '.wav'))
            engine.runAndWait()
            wav_path = output_path.replace('.mp3', '.wav')
            subprocess.run([
                'ffmpeg', '-i', wav_path, '-codec:a', 'libmp3lame',
                '-qscale:a', '2', output_path, '-y'
            ], check=True, capture_output=True)
            os.remove(wav_path)
            logger.info(f"Fallback voiceover saved: {output_path}")
            return output_path
        except Exception as e2:
            logger.warning(f"pyttsx3 failed: {e2} — using gTTS fallback")
            from gtts import gTTS
            tts = gTTS(text=script, lang='en', slow=False)
            tts.save(output_path)
            logger.info(f"gTTS voiceover saved: {output_path}")
            return output_path
