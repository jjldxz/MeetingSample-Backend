ERROR = {
    'INPUT': {
        'code': 20001,
        'message': 'invalid request data',
        'data': 'invalid request data',
    },
    'REGISTER': {
        'code': 20002,
        'data': '',
        'message': 'failed to register user'
    },
    'USER_NOT_FOUND': {
        'code': 20003,
        'data': '',
        'message': 'invalid username'
    },
    'INVALID_PASSWORD': {
        'code': 20004,
        'data': '',
        'message': 'invalid password'
    },
    'NEED_ENVIRONMENT': {
        'code': 20005,
        'data': '',
        'message': 'not set environment'
    },
    'TOKEN_EXP': {
        'code': 20006,
        'data': '',
        'message': 'token expired'
    },
    'TOKEN_INVALID': {
        'code': 20007,
        'data': '',
        'message': 'invalid token'
    },
    'INTERNAL': {
        'code': 20008,
        'data': '',
        'message': 'internal error'
    },
    'NO_PERMISSION': {
        'code': 30009,
        'message': 'not permission'
    },

    # meeting
    'MEETING_INPUT': {
        'code': 30001,
        'data': '',
        'message': 'invalid request data'
    },
    'NEW_MEETING_FAILED': {
        'code': 30002,
        'data': '',
        'message': 'failed to create meeting'
    },
    'MEETING_NOT_FOUND': {
        'code': 30003,
        'data': '',
        'message': 'meeting not found'
    },
    'MEETING_INFO_DATABASE': {
        'code': 30005,
        'data': '',
        'message': 'failed to access database'
    },
    'MEETING_IS_OVER': {
        'code': 30006,
        'data': '',
        'message': 'meeting is over'
    },
    'MEETING_NOT_START': {
        'code': 30007,
        'message': 'meeting is not start'
    },
    'IS_SHARED': {
        'code': 30008,
        'message': 'other is sharing'
    },
    'NOT_SHARE': {
        'code': 30009,
        'message': 'not sharing'
    },
    'NOT_PERMISSION_STOP': {
        'code': 30010,
        'message': 'not permission to stop meeting'
    },

    # user
    'CHANGE_PASSWORD_FAILED': {
        'code': 40001,
        'data': '',
        'message': 'failed to change password'
    },
    'USER_INFO_DATABASE': {
        'code': 40002,
        'data': '',
        'message': 'failed to access database'
    },

    # poll
    'POLL_INPUT': {
        'code': 50001,
        'data': '',
        'message': 'invalid request data'
    },
    'GET_POLL_FAILED': {
        'code': 50002,
        'data': '',
        'message': 'failed to get poll list'
    },
    'POLL_NOT_FOUND': {
        'code': 50003,
        'data': '',
        'message': 'poll not found'
    },
    'POLL_NOT_HOST': {
        'code': 50004,
        'data': '',
        'message': 'user has no permission to operate poll'
    },
    'POLL_INFO_DATABASE': {
        'code': 50005,
        'data': '',
        'message': 'failed to access database'
    },
    'POLL_ALREADY_START': {
        'code': 50006,
        'data': '',
        'message': 'poll already start'
    },
    'POLL_NOT_START': {
        'code': 50007,
        'data': '',
        'message': 'poll not start'
    },
    'POLL_EXIST': {
        'code': 50008,
        'data': '',
        'message': 'poll already exist'
    },
    'POLL_ALREADY_DONE': {
        'code': 50009,
        'data': '',
        'message': 'poll already done'
    },

    # Group
    'GROUP_ALREADY_START': {
        'code': 60000,
        'data': '',
        'message': 'group already start'
    },
    'GROUP_NOT_FOUND': {
        'code': 60001,
        'data': '',
        'message': 'group not found'
    },
}
