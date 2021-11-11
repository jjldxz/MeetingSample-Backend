import json
from urllib.parse import urljoin

import requests

from meeting_sample.settings import APP_KEY, LVB_HOST


def stop_lvb_room(token: str) -> int:
    meeting_id_url = urljoin(LVB_HOST, '/api/client/get_internal_room')
    stop_url = urljoin(LVB_HOST, '/api/client/stop_room')
    header = {
        'Content-Type': 'application/json',
        'app-key': APP_KEY,
        'token': token,
    }
    resp = requests.get(meeting_id_url, headers=header)
    if resp.status_code != 200:
        raise RuntimeError(resp.content)

    resp = requests.post(stop_url, headers=header, data=resp.content)
    if resp.status_code != 200:
        raise RuntimeError(resp.content)

    return json.loads(resp.content)['room_id']
