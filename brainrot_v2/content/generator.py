import anthropic
import logging
from core.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCRIPT_SYSTEM = """You write YouTube Shorts scripts. Educational facts delivered with brain rot Gen-Z energy.

Rules:
- Max 120 words
- First sentence is the hook — shocking, punchy, all caps energy
- Short sentences only — 8 words max each
- Sound genuinely shocked at the facts
- Real accurate educational information
- End with a call to follow
- No hashtags, no stage directions, just the spoken words
- Style: {style}"""

META_SYSTEM = """Generate YouTube Shorts metadata. Respond EXACTLY in this format, nothing else:
TITLE: [viral title max 60 chars with emojis]
DESCRIPTION: [2 sentences + hashtags]
TAGS: [tag1,tag2,tag3,tag4,tag5,tag6,tag7,tag8,tag9,tag10]"""


def generate_script(topic: str, style: str) -> str:
    try:
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=SCRIPT_SYSTEM.format(style=style),
            messages=[{"role": "user", "content": f"Topic: {topic}"}]
        )
        script = r.content[0].text.strip()
        logger.info(f"Script generated ({len(script)} chars)")
        return script
    except Exception as e:
        logger.error(f"Script gen error: {e}")
        return f"BRO WAIT. {topic.upper()}. This is actually insane. Nobody talks about this. The facts will blow your mind completely. Science is genuinely unhinged. Follow for more mind blowing facts daily."


def generate_metadata(script: str, channel_tags: list) -> dict:
    try:
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            system=META_SYSTEM,
            messages=[{"role": "user", "content": f"Script: {script[:400]}"}]
        )
        raw = r.content[0].text.strip()
        lines = raw.split('\n')
        meta = {"title": "", "description": "", "tags": channel_tags}

        for line in lines:
            if line.startswith("TITLE:"):
                meta["title"] = line.replace("TITLE:", "").strip()[:100]
            elif line.startswith("DESCRIPTION:"):
                meta["description"] = line.replace("DESCRIPTION:", "").strip()[:500]
            elif line.startswith("TAGS:"):
                generated_tags = [t.strip() for t in line.replace("TAGS:", "").split(",")]
                meta["tags"] = list(set(channel_tags + generated_tags))[:30]

        logger.info(f"Metadata: {meta['title']}")
        return meta
    except Exception as e:
        logger.error(f"Metadata gen error: {e}")
        return {
            "title": "🔥 This Will BLOW Your Mind #shorts",
            "description": "Facts they never taught you. #shorts #viral #educational #facts #mindblowing",
            "tags": channel_tags
        }
