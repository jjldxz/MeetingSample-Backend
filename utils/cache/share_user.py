import random

from meeting_sample.settings import REDIS_PREFIX
from utils.cache.connection import client

_KEY = f'{REDIS_PREFIX}:share_user'


def generate():
    _id = random.randint(100000000, 999999999)

    values = client.lrange(_KEY, 0, -1)
    while _id in [int(x) for x in values]:
        _id = generate()

    client.lpush(_KEY, _id)
    return _id


def remove(share_user_id: int):
    client.lrem(_KEY, 0, share_user_id)
