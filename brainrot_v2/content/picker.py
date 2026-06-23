import random
import logging
from core.channels import CHANNELS

logger = logging.getLogger(__name__)

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except Exception:
    PYTRENDS_AVAILABLE = False


def get_trending_topics(limit=5):
    if not PYTRENDS_AVAILABLE:
        return []
    try:
        pt = TrendReq(hl='en-US', tz=360)
        df = pt.trending_searches(pn='united_states')
        return df[0].tolist()[:limit]
    except Exception as e:
        logger.warning(f"Trends fetch failed: {e}")
        return []


def pick_topic(channel_id: str) -> dict:
    channel = CHANNELS.get(channel_id)
    if not channel:
        raise ValueError(f"Unknown channel: {channel_id}")

    topic_bank = channel["topics"]
    trending = get_trending_topics(limit=3)

    if trending and random.random() < 0.3:
        topic = random.choice(trending)
        source = "trending"
    else:
        topic = random.choice(topic_bank)
        source = "bank"

    logger.info(f"[{channel['name']}] Topic ({source}): {topic}")
    return {
        "channel_id": channel_id,
        "channel": channel,
        "topic": topic,
        "source": source,
    }
