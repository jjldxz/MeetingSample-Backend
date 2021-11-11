import datetime
import logging
from typing import List

from meeting_sample.settings import REDIS_PREFIX
from utils.cache.connection import client

logger = logging.getLogger(__name__)

DELAY_QUEUE = REDIS_PREFIX + ':delay_queue'


def push(meeting: int, expire_seconds: int) -> None:
    mapping = {meeting: expire_seconds}
    client.zadd(DELAY_QUEUE, mapping)


def pop(meeting: int) -> None:
    client.zrem(DELAY_QUEUE, str(meeting))


def retrieve() -> List[int]:
    max_score = int(datetime.datetime.utcnow().timestamp())
    val = client.zrangebyscore(DELAY_QUEUE, 0, max_score)
    return [int(v) for v in val]
