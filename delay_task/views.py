import logging
import threading
import time

from django.db import close_old_connections

from meeting.views import StopMeetingAPI
from utils import cache

thread_id = 0
refresh_interval = 20  # 20 seconds
logger = logging.getLogger(__name__)


# Create your views here.
def start_delay_task():
    if thread_id != 0:
        logger.warning(f'delay task is already running, TID: {thread_id}')
        return

    threading.Thread(target=__delay_task, name='Delay Task', daemon=True).start()
    logger.info(f'start delay task')


def __delay_task():
    global thread_id
    thread_id = threading.get_ident()
    logger.info(f'delay task started')

    while True:
        try:
            for meeting in cache.delay_queue.retrieve():
                close_old_connections()
                logger.info(f'to close meeting: {meeting}')
                StopMeetingAPI.stop_meeting(meeting, None)
            else:
                logger.debug('empty delay queue')
        except Exception as e:
            logger.warning(f'ignore exception: {e}')
        time.sleep(refresh_interval)
