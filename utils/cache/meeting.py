from meeting_sample.settings import REDIS_PREFIX
from utils.cache.connection import client

MEETING_KEY = f'{REDIS_PREFIX}:meeting:'


def open_meeting(meeting_id: int, ex: int):
    key = MEETING_KEY + str(meeting_id)

    value = {
        'sharing_user': 0,
    }
    client.hset(key, mapping=value)
    client.expire(key, ex)


def close_meeting(meeting_id: int):
    key = MEETING_KEY + str(meeting_id)
    client.delete(key)


def get_sharing_user(meeting_id: int) -> int:
    key = MEETING_KEY + str(meeting_id)
    val = client.hget(key, 'sharing_user')
    if val is None:
        return -1
    return int(val)


def start_share(meeting_id: int, user_id: int):
    key = MEETING_KEY + str(meeting_id)
    client.hset(key, 'sharing_user', user_id)


def stop_share(meeting_id: int):
    key = MEETING_KEY + str(meeting_id)
    client.hset(key, 'sharing_user', 0)


def is_meeting_open(meeting_id: int) -> bool:
    key = MEETING_KEY + str(meeting_id)
    return bool(client.exists(key))
