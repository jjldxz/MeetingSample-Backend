# Create your views here.
import logging

from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, APIException, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from user.serializers import UserInfoOut, ChangePwdIn, UpdateUserInfoIn, ChangePwdOut
from utils.errors import ERROR
from utils.resp import r200

logger = logging.getLogger(__name__)


class UserInfoAPI(APIView):
    """
    Get user info
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(responses={200: UserInfoOut}, tags=['user'])
    def get(self, request, *args, **kwargs):
        logger.info(f'user {request.user} get info')
        data_out = UserInfoOut(instance=request.user)
        return r200(data_out.data)


class ChangePwdAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=ChangePwdIn, responses={200: ChangePwdOut}, tags=['user'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[change password] data: {request.data}')

        data_in = ChangePwdIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        old_password = data_in.validated_data['old_password']
        new_password = data_in.validated_data['new_password']
        try:
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save(update_fields=['password'])
            else:
                logger.error('Invalid old password')
                err = ERROR['INVALID_PASSWORD']
                raise AuthenticationFailed(err)
        except Exception as e:
            logger.error(f'Failed to change password: {e}')
            err = ERROR['CHANGE_PASSWORD_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        data_out = ChangePwdOut(instance=dict(success=True))
        logger.info(f'[change password] id: {request.user} success: {data_out.data}')
        return r200(data=data_out.data)


class UpdateInfoAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=UpdateUserInfoIn, responses={200: UserInfoOut}, tags=['user'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[update info] data: {request.data}')

        data_in = UpdateUserInfoIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            raise ValidationError(data_in.errors)

        try:
            user = User.objects.filter(id=request.user.id)
            user.update(**data_in.validated_data)
        except Exception as e:
            logger.error(f'Failed to update user info: {e}')
            err = ERROR('USER_INFO_DATABASE')
            err['data'] = str(e)
            raise APIException(err)

        data_out = UserInfoOut(instance=user[0])
        logger.info(f'[update info] id: {user} success {data_out.data}')
        return r200(data=data_out.data)
