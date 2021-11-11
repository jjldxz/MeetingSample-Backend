import json
from typing import Dict, Optional

from meeting_sample.settings import REDIS_PREFIX
from utils.cache.connection import client, acquire_lock_with_timeout, release_lock

MEETING_GROUP_KEY = f'{REDIS_PREFIX}:meeting:group:'


# @debug_time
def open_group(meeting_id: int, group_info: dict, ex: int) -> bool:
    """
    meeting_id: Meeting ID
    """
    lock_name = f'new-group-lock-{meeting_id}'
    key = MEETING_GROUP_KEY + str(meeting_id)

    info = json.dumps(group_info)

    locker = acquire_lock_with_timeout(lock_name, meeting_id, 10, 10)
    if locker is None:
        raise RuntimeError(f'can not lock room: {lock_name}')
    val = client.set(key, info, nx=True, ex=ex)
    release_lock(lock_name, locker)

    if val:
        return True

    # key already set == group already start
    return False


# @debug_time
def close_group(meeting_id: int):
    """
    meeting_id: Meeting ID
    """
    key = MEETING_GROUP_KEY + str(meeting_id)
    client.delete(key)


def get_group_info(meeting_id) -> Optional[Dict]:
    key = MEETING_GROUP_KEY + str(meeting_id)
    val = client.get(key)
    if val is None:
        return None

    return json.loads(val)


def update_group_info(meeting_id: int, group_info: Dict) -> bool:
    key = MEETING_GROUP_KEY + str(meeting_id)

    info = json.dumps(group_info)
    val = client.set(key, info, xx=True)
    if val:
        return True
    # not found the key
    return False
