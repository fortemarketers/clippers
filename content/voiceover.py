import asyncio
import os
import logging

logger = logging.getLogger(__name__)


async def _generate(script: str, voice: str, rate: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(script, voice=voice, rate=rate)
    await communicate.save(output_path)


def generate_voiceover(script: str, voice: str, rate: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    asyncio.run(_generate(script, voice, rate, output_path))
    logger.info(f"Voiceover saved: {output_path}")
    return output_path
