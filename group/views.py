import logging

# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from group.serializers import StartIn, BaseOut, MoveMemberIn, GroupDetailIn, GroupDetailOut
from meeting.models import Meeting
from utils import cache
from utils.errors import ERROR
from utils.resp import r200

logger = logging.getLogger(__file__)


class GroupStartAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=StartIn, tags=['group'], responses={200: BaseOut})
    def post(self, request, *args, **kwargs):
        """
        Start a group
        """
        logger.info(f'[GroupStartAPI] user:{request.user.id} start a group: {request.data}')

        data_in = StartIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise exceptions.ValidationError(err)
        number = data_in.validated_data['number']
        group_info = data_in.validated_data['group']

        try:
            meeting = Meeting.objects.get(call_number=number)
        except ObjectDoesNotExist:
            logger.error(f'invalid meeting: {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = f'invalid meeting number: {number}'
            raise exceptions.NotFound(err)

        if meeting.status != Meeting.RoomStatus.ONGOING.value:
            logger.warning(f'meeting not start')
            err = ERROR['MEETING_NOT_START']
            err['data'] = f'meeting not start: {number}'
            raise exceptions.ValidationError(err)

        if meeting.owner != request.user:
            logger.error(f'no permission to start meeting')
            err = ERROR['NO_PERMISSION']
            err['data'] = f'not the owner of this meeting'
            raise exceptions.PermissionDenied(err)

        ex = int(meeting.end_at.timestamp()) + 8 * 3600
        if not cache.group.open_group(number, group_info, ex):
            logger.error(f'meeting: {number} already start group')
            err = ERROR['GROUP_ALREADY_START']
            err['data'] = f'group already start for meeting: {number}'
            raise exceptions.ValidationError(err)

        out = BaseOut(instance={'success': True})
        logger.info(f'[GroupStartAPI] success: {out.data}')
        return r200(out.data)


class GroupStopAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=GroupDetailIn, tags=['group'], responses={200: BaseOut})
    def post(self, request, *args, **kwargs):
        """
        Stop group
        """
        logger.info(f'[GroupStopAPI] user:{request.user.id} stop group: {request.data}')

        data_in = GroupDetailIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise exceptions.ValidationError(err)
        number = data_in.validated_data['number']

        try:
            meeting = Meeting.objects.get(call_number=number)
        except ObjectDoesNotExist:
            logger.error(f'invalid meeting: {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = f'invalid meeting number: {number}'
            raise exceptions.NotFound(err)

        if meeting.status != Meeting.RoomStatus.ONGOING.value:
            logger.warning(f'meeting not start')
            err = ERROR['MEETING_NOT_START']
            err['data'] = f'meeting not start: {number}'
            raise exceptions.ValidationError(err)

        if meeting.owner != request.user:
            logger.error(f'no permission to start meeting')
            err = ERROR['NO_PERMISSION']
            err['data'] = f'not the owner of this meeting'
            raise exceptions.PermissionDenied(err)

        cache.group.close_group(number)

        out = BaseOut(instance={'success': True})
        logger.info(f'[GroupStopAPI] success: {out.data}')
        return r200(out.data)


class MoveMemberAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=MoveMemberIn, tags=['group'], responses={200: BaseOut})
    def post(self, request, *args, **kwargs):
        """
        Move a group member to another group
        """
        logger.info(f'[MoveMemberAPI] user:{request.user.id} move somebody to new group: {request.data}')

        data_in = MoveMemberIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise exceptions.ValidationError(err)

        number = data_in.validated_data['number']
        members = data_in.validated_data['members']
        from_group = data_in.validated_data['from_group']
        to_group = data_in.validated_data['to_group']

        try:
            Meeting.objects.get(call_number=number, status=Meeting.RoomStatus.ONGOING)
        except ObjectDoesNotExist:
            logger.error(f'invalid meeting ID or status {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = 'invalid meeting'
            raise exceptions.ValidationError(err)

        try:
            group_info = cache.group.get_group_info(number)
        except Exception as e:
            logger.error(f'failed to get group info: {e}')
            err = ERROR['INTERNAL']
            err['data'] = 'failed to get group info'
            raise exceptions.APIException(err)

        if group_info is None:
            logger.error(f'not find group info for meeting: {number}')
            err = ERROR['GROUP_NOT_FOUND']
            err['data'] = f'not found group info for meeting: {number}'
            raise exceptions.NotFound(err)

        for group in group_info:
            if group is None:
                logger.warning(f'invalid group in group info list')
                continue
            if group['id'] == from_group:
                for member in members:
                    if member in group['users']:
                        group['users'].remove(member)
            if group['id'] == to_group:
                group['users'].extend(members)

        try:
            updated = cache.group.update_group_info(number, group_info)
        except Exception as e:
            logger.error(f'failed to update group info: {e}')
            err = ERROR['INTERNAL']
            err['data'] = 'failed to update group info'
            raise exceptions.APIException(err)

        if not updated:
            logger.error(f'invalid meeting : {number}')
            err = ERROR['MEETING_NOT_FOUND']
            err['data'] = 'invalid meeting'
            raise exceptions.APIException(err)

        out = BaseOut(instance={'success': True})
        logger.info(f'[MoveMemberAPI] success: {out.data}')
        return r200(out.data)


class GroupDetailAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=GroupDetailIn, tags=['group'], responses={200: GroupDetailOut})
    def post(self, request, *args, **kwargs):
        """
        Move a group member to another group
        """
        logger.info(f'[GroupDetailAPI] user:{request.user.id} get group detail: {request.data}')

        data_in = GroupDetailIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise exceptions.ValidationError(err)
        number = data_in.validated_data['number']
        try:
            group_info = cache.group.get_group_info(number)
        except Exception as e:
            logger.error(f'failed to get group info: {e}')
            err = ERROR['INTERNAL']
            err['data'] = 'failed to get group info'
            raise exceptions.APIException(err)

        out = GroupDetailOut(instance={'group': group_info})
        logger.info(f'[GroupDetailAPI] success: {out.data}')
        return r200(out.data)
