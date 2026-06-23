import random
import logging
import json
import os
from core.channels import CHANNELS
import anthropic
from core.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

USED_TOPICS_FILE = "/tmp/used_topics.json"


def load_used(channel_id):
    try:
        if os.path.exists(USED_TOPICS_FILE):
            with open(USED_TOPICS_FILE) as f:
                return json.load(f).get(channel_id, [])
    except Exception:
        pass
    return []


def save_used(channel_id, used):
    try:
        data = {}
        if os.path.exists(USED_TOPICS_FILE):
            with open(USED_TOPICS_FILE) as f:
                data = json.load(f)
        data[channel_id] = used[-200:]
        with open(USED_TOPICS_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def generate_fresh_topics(niche: str, existing: list) -> list:
    try:
        prompt = f"""Generate 20 brand new viral YouTube Shorts topic ideas for a {niche} educational channel.
Each topic must be a short punchy fact or question (max 8 words).
Do NOT repeat any of these: {existing[-20:]}
Return ONLY a JSON array of 20 strings, nothing else."""
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = r.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        topics = json.loads(raw)
        logger.info(f"Generated {len(topics)} fresh topics for {niche}")
        return topics
    except Exception as e:
        logger.error(f"Topic generation failed: {e}")
        return [f"mind blowing {niche} fact you never knew",
                f"shocking {niche} secret exposed",
                f"insane {niche} truth nobody talks about"]


def pick_topic(channel_id: str) -> dict:
    channel = CHANNELS.get(channel_id)
    if not channel:
        raise ValueError(f"Unknown channel: {channel_id}")

    used = load_used(channel_id)
    bank = channel["topics"].copy()

    available = [t for t in bank if t not in used]

    if len(available) < 3:
        logger.info(f"[{channel['name']}] Topic bank low — generating fresh topics via Claude")
        fresh = generate_fresh_topics(channel["niche"], used)
        available = [t for t in fresh if t not in used]
        if not available:
            available = fresh

    topic = random.choice(available)
    used.append(topic)
    save_used(channel_id, used)

    logger.info(f"[{channel['name']}] Topic: {topic} ({len(available)-1} remaining)")
    return {
        "channel_id": channel_id,
        "channel": channel,
        "topic": topic,
        "source": "bank",
    }
