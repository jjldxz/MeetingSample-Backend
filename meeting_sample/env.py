import os

DATABASE_URL = os.getenv('DATABASE_URL', None)
DB_CONN_MAX_AGE = int(os.getenv('DB_CONN_MAX_AGE', 3600))

APP_KEY = os.getenv('APP_KEY', None)
APP_SECRET = os.getenv('APP_SECRET', None)

SALT = os.getenv('SALT', None)

REDIS_HOST = os.getenv('REDIS_HOST', None)
REDIS_CLUSTER_ENABLED = (os.getenv('REDIS_CLUSTER_ENABLED', 'false').lower() == 'true')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_PREFIX = os.getenv('REDIS_PREFIX', '0')

SENTRY_DSN = os.getenv('SENTRY_DSN', 'http://f198a73df01344e48da8aa8511598bf7@192.168.7.77:9000/4')

LVB_HOST = os.getenv('LVB_HOST', None)
