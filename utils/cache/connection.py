import logging
import os
import time
from typing import Optional

import redis
from rediscluster import RedisCluster

from meeting_sample.settings import REDIS_HOST, REDIS_CLUSTER_ENABLED, REDIS_PREFIX, REDIS_PASSWORD

logger = logging.getLogger(__name__)

DEFAULT_EXPIRE_TIME = os.getenv('CACHE_EXPIRE', 8 * 60 * 60)  # 8 hours
VALID_SHADOW_USER_KEY = f'{REDIS_PREFIX}:valid_shadow_user'

if REDIS_HOST is None:
    raise RuntimeError('need set redis host')

client = None
if REDIS_CLUSTER_ENABLED:
    startup_nodes = []
    for x in REDIS_HOST.split(','):
        y = x.replace('redis://', '').split(':')
        startup_nodes.append({'host': y[0], 'port': int(y[1])})
    client = RedisCluster(startup_nodes=startup_nodes, decode_responses=False, max_connections=1024,
                          password=REDIS_PASSWORD, skip_full_coverage_check=True)
    logger.info(f'Connect to Redis cluster: {startup_nodes}')
else:
    pool = redis.ConnectionPool.from_url(REDIS_HOST)
    client = redis.Redis(connection_pool=pool)
    logger.info(f'Connect to Redis single server: {REDIS_HOST}')


def debug_time(func):
    def wrapper(*args, **kwargs):
        s = time.time()
        data = func(*args, **kwargs)
        logger.debug(f'Call {func.__name__} cost: {time.time() - s} second')
        return data

    return wrapper


def acquire_lock_with_timeout(lock_name, room_id, acquire_timeout=3, lock_timeout=1) -> Optional[str]:
    """
    lock_timeout: 1 seconds
    """
    identifier = f'{room_id}-lock'
    end = time.time() + acquire_timeout
    while time.time() < end:
        if client.set(lock_name, identifier, ex=lock_timeout, nx=True):
            return identifier
        time.sleep(0.001)
    return None


def release_lock(lock_name, identifier):
    unlock_script = """
        if redis.call("get",KEYS[1]) == ARGV[1] then
            return redis.call("del",KEYS[1])
        else
            return 0
        end
        """
    unlock = client.register_script(unlock_script)
    result = unlock(keys=[lock_name], args=[identifier])
    logger.debug(f'unlock: {lock_name} result: {result}')
