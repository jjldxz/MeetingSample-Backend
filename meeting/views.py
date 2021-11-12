# Create your views here.
import datetime
import logging
import random
from calendar import timegm

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, APIException, NotFound, NotAcceptable, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from meeting.models import Meeting
from meeting.serializers import NewMeetingIn, BaseMeetingOut, MeetingInfoIn, MeetingInfoOut, MeetingListIn, \
    NewMeetingOut, DelMeetingIn, JoinMeetingOut, JoinMeetingIn, MeetingIn
from meeting_sample.settings import APP_KEY, APP_SECRET, LVB_HOST
from utils import cache, lvb
from utils import encryption
from utils.errors import ERROR
from utils.resp import r200

logger = logging.getLogger(__name__)


class NewMeetingAPI(APIView):
    """
    Create a new meeting
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=NewMeetingIn, responses={200: NewMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[NewMeetingAPI] user: {request.user.id} create meeting: {request.data}')

        data_in = NewMeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        begin_at = data_in.validated_data.pop('begin_at')
        end_at = data_in.validated_data.pop('end_at')
        mute_type = data_in.validated_data.pop('mute_type', Meeting.MuteType.UNMUTE)

        try:
            meeting = Meeting.objects.create(**data_in.validated_data, begin_at=begin_at, end_at=end_at,
                                             mute_type=mute_type, owner=request.user,
                                             call_number=self.__gen_call_number(),
                                             created=datetime.datetime.utcnow())
        except Exception as e:
            logger.error(f'failed to create meeting: {e}')
            err = ERROR['NEW_MEETING_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        out = NewMeetingOut(instance=meeting)
        logger.info(f'[NewMeetingAPI] success: {out.data}')
        return r200(out.data)

    def __gen_call_number(self):
        random.seed(datetime.datetime.utcnow().timestamp())
        b = random.randint(1, 9)
        o = random.randint(0, 1e8 - 1)
        call_number = int(b * 1e8 + o)

        if Meeting.objects.filter(call_number=call_number).count() > 0:
            logger.warning(f'{call_number} is exist, re-generate call number')
            return self.__gen_call_number()
        logger.info(f'generate call number:{call_number}')
        return call_number


class DelMeetingAPI(APIView):
    """
    Delete a new meeting by meeting ID.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=DelMeetingIn, responses={200: BaseMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[DelMeetingAPI] user: {request.user.id} delete meeting: {request.data}')

        data_in = DelMeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        meeting_ids = data_in.validated_data['meetings']

        try:
            Meeting.objects.filter(call_number__in=meeting_ids, owner=request.user).delete()
        except Exception as e:
            logger.error(f'failed to delete meetings: {e}')
            err = ERROR['MEETING_INFO_DATABASE']
            err['data'] = str(e)
            raise NotFound(err)

        logger.info('[DelMeetingAPI] success')
        out = BaseMeetingOut(instance=dict(success=True))
        return r200(out.data)


class MeetingInfoAPI(APIView):
    """
    Delete a new meeting by meeting ID.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=MeetingInfoIn, responses={200: MeetingInfoOut}, tags=['meeting'])
    def get(self, request, *args, **kwargs):
        logger.info(f'[MeetingInfoAPI] user: {request.user.id} data: {request.query_params}')

        data_in = MeetingInfoIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        try:
            meeting = Meeting.objects.get(call_number=data_in.validated_data['number'])
        except ObjectDoesNotExist:
            logger.error(f'invalid query param: {data_in.validated_data}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = f'invalid query param: {data_in.validated_data}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get meeting: {e}')
            err = ERROR['MEETING_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        out = MeetingInfoOut(instance=meeting)
        logger.info(f'[MeetingInfoAPI] success: {out.data}')
        return r200(out.data)


class ListMeetingAPI(APIView):
    """
    Get user's meeting list in a period.
    which's begin time between begin_at and endAt.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=MeetingListIn, responses={200: MeetingInfoOut}, tags=['meeting'])
    def get(self, request, *args, **kwargs):
        logger.info(f'[ListMeetingAPI] user: {request.user.id} get new and ongoing meetings: {request.query_params}')

        data_in = MeetingListIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        try:
            meetings = Meeting.objects.filter(owner=request.user).order_by('-created')
            if 'beginAt' in data_in.validated_data:
                meetings = meetings.filter(begin_at__gte=data_in.validated_data['beginAt'])
            if 'endAt' in data_in.validated_data:
                meetings = meetings.filter(begin_at__lte=data_in.validated_data['endAt'])
        except Exception as e:
            logger.error(f'failed to get meeting: {e}')
            err = ERROR['MEETING_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        out = MeetingInfoOut(instance=meetings, many=True)
        logger.info(f'[ListMeetingAPI] success: {meetings.count()}')
        return r200(out.data)


class JoinMeetingAPI(APIView):
    """
    Join meeting by meeting ID.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=JoinMeetingIn, responses={200: JoinMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[JoinMeetingAPI] user: {request.user.id} join meeting: {request.data}')

        data_in = JoinMeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data['number']

        try:
            meeting = Meeting.objects.get(call_number=number)
        except ObjectDoesNotExist:
            logger.error(f'invalid meeting number: {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = f'meeting number: {number}'
            raise NotFound(err)

        if meeting.password is not None:
            if 'password' not in data_in.validated_data:
                logger.error('need password')
                err = ERROR['MEETING_INPUT']
                err['data'] = 'need password'
                raise ValidationError(err)
            if meeting.password != data_in.validated_data['password']:
                logger.error('invalid meeting password')
                err = ERROR['INVALID_PASSWORD']
                err['data'] = 'password not match'
                raise ValidationError(err)

        if meeting.end_at + datetime.timedelta(minutes=1) < datetime.datetime.utcnow():
            logger.warning('meeting is over')
            err = ERROR['MEETING_IS_OVER']
            err['data'] = f'meeting is over: {meeting.end_at}'
            raise APIException(err)

        if meeting.begin_at - datetime.timedelta(minutes=1) > datetime.datetime.utcnow():
            logger.warning('meeting is not start')
            err = ERROR['MEETING_NOT_START']
            err['data'] = f'meeting is not start: {meeting.begin_at}'
            raise APIException(err)

        tm_now = timegm(datetime.datetime.utcnow().utctimetuple())
        duration = int((meeting.end_at - meeting.begin_at).total_seconds())
        token_src = f'{APP_KEY}_{meeting.call_number}_{request.user.id}_{duration}_{tm_now}'
        lvb_token = encryption.encode(APP_SECRET, token_src)

        if meeting.status == Meeting.RoomStatus.NEW:
            meeting.share_user_id = cache.share_user.generate()
            try:
                Meeting.objects.filter(call_number=number). \
                    update(status=Meeting.RoomStatus.ONGOING,
                           actually_begin_at=datetime.datetime.utcnow(),
                           share_user_id=meeting.share_user_id)
            except Exception as e:
                logger.error(f'failed to update meeting status: {e}')
                err = ERROR['MEETING_INFO_DATABASE']
                err['data'] = str(e)
                raise APIException(err)

            ex = meeting.end_at - datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
            cache.open_meeting(number, ex)
            cache.delay_queue.push(number, int(meeting.end_at.timestamp()))
            logger.info(f'start meeting in cache')

        try:
            group_info = cache.group.get_group_info(meeting.call_number)
        except Exception as e:
            logger.error(f'failed to get group info: {e}')
            err = ERROR['INTERNAL']
            err['data'] = 'failed to get group info'
            raise APIException(err)

        share_user_token_src = f'{APP_KEY}_{meeting.call_number}_{meeting.share_user_id}_{duration}_{tm_now}'
        share_user_token = encryption.encode(APP_SECRET, share_user_token_src)
        out = JoinMeetingOut(instance=dict(token=lvb_token, app_key=APP_KEY,
                                           room_id=meeting.call_number,
                                           share_user_id=meeting.share_user_id,
                                           share_user_token=share_user_token,
                                           is_breakout=group_info is not None
                                           ))
        logger.info(f'[JoinMeetingAPI] success: {out.data}')
        return r200(out.data)


class StopMeetingAPI(APIView):
    """
    Stop meeting by meeting ID.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MeetingIn, responses={200: BaseMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[StopMeetingAPI] user: {request.user.id} join meeting: {request.data}')

        data_in = MeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data['number']

        try:
            stopped = self.stop_meeting(number, request.user)
        except Exception as e:
            logger.error(f'failed to stop meeting: {e}')

        out = BaseMeetingOut(dict(success=stopped))
        logger.info(f'[StopMeetingAPI] success: {out.data}')
        return r200(out.data)

    @staticmethod
    def stop_meeting(number: int, invoker: User) -> bool:
        stopped = True
        try:
            meeting = Meeting.objects.get(call_number=number)
        except ObjectDoesNotExist:
            logger.error(f'invalid meeting number: {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = f'meeting number: {number}'
            raise NotFound(err)

        if invoker is not None and meeting.owner != invoker:
            logger.error(f'no permission to stop meeting')
            err = ERROR['NOT_PERMISSION_STOP']
            err['data'] = f'owner ID: {meeting.owner.id}'
            raise PermissionDenied(err)

        if meeting.status != Meeting.RoomStatus.CLOSED:
            if StopMeetingAPI.stop_lvb_room(meeting, number):
                try:
                    Meeting.objects.filter(call_number=number). \
                        update(status=Meeting.RoomStatus.CLOSED,
                               closed_by=invoker,
                               actually_end_at=datetime.datetime.utcnow())
                except Exception as e:
                    logger.error(f'failed to update meeting status: {e}')
                    err = ERROR['MEETING_INFO_DATABASE']
                    err['data'] = str(e)
                    raise APIException(err)

        # if call LVB error, stop it again
        if cache.is_meeting_open(number):
            stopped = StopMeetingAPI.stop_lvb_room(meeting, number)
        return stopped

    @staticmethod
    def stop_lvb_room(meeting: Meeting, number: int) -> bool:
        if LVB_HOST is None:
            logger.error(f'not set LVB host')
            return False
        else:
            tm_now = timegm(datetime.datetime.utcnow().utctimetuple())
            duration = int((meeting.end_at - meeting.begin_at).total_seconds())
            token_src = f'{APP_KEY}_{meeting.call_number}_{meeting.owner.id}_{duration}_{tm_now}'
            lvb_token = encryption.encode(APP_SECRET, token_src)

            try:
                sts, lvb_room_id = lvb.stop_lvb_room(lvb_token)
            except Exception as e:
                logger.error(f'call lvb stop error: {e}')
                return False
            logger.info(f'success: {sts}, close lvb room: {lvb_room_id}')

        cache.close_meeting(number)
        cache.delay_queue.pop(number)
        cache.share_user.remove(meeting.share_user_id)
        cache.group.close_group(meeting.call_number)
        logger.info(f'stop meeting in cache')
        return True


class StartShareAPI(APIView):
    """
    User request to start share
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MeetingIn, responses={200: BaseMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[StartShareAPI] user: {request.user.id} request to start share: {request.data}')

        data_in = MeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data['number']

        share_user = cache.get_sharing_user(number)
        if -1 == share_user:
            logger.error(f'meeting: {number} not start')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = 'not found ongoing meeting'
            raise NotFound(err)

        if share_user > 0 and share_user != request.user.id:
            err = ERROR['IS_SHARED']
            err['data'] = f'user {share_user} is sharing'
            raise NotAcceptable(err)

        cache.start_share(number, request.user.id)

        out = BaseMeetingOut(instance=dict(success=True))
        logger.info(f'[StartShareAPI] success: meeting: {number}, user: {request.user.id}')
        return r200(out.data)


class StopShareAPI(APIView):
    """
    User stop share
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MeetingIn, responses={200: BaseMeetingOut}, tags=['meeting'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[StopShareAPI] user: {request.user.id} request to stop share: {request.data}')

        data_in = MeetingIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['MEETING_INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data['number']

        share_user = cache.get_sharing_user(number)
        if share_user != request.user.id:
            logger.error(f'share user not match request user')
            err = ERROR['NOT_SHARE']
            err['data'] = f'sharing user is {share_user}'
            raise PermissionDenied(err)

        cache.stop_share(number)

        out = BaseMeetingOut(instance=dict(success=True))
        logger.info(f'[StopShareAPI] success: {out.data}')
        return r200(out.data)
