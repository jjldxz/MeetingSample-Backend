import logging
from calendar import timegm
from datetime import datetime
from typing import Dict

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, APIException, NotFound, AuthenticationFailed, ParseError
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_encode_handler

from common.serializers import *
from meeting_sample.env import SALT
from utils import encryption
from utils.errors import ERROR
from utils.resp import r200

logger = logging.getLogger(__name__)


def generate_token(user: User) -> Dict:
    if SALT is None:
        logger.error('need environment SALT')
        err = ERROR['NEED_ENVIRONMENT']
        err['data'] = 'need environment SALT'
        raise APIException(err)

    payload = jwt_payload_handler(user)
    refresh_payload = {
        'user_id': user.pk,
        'exp': timegm((datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA).utctimetuple()),
    }

    result = {
        'token': jwt_encode_handler(payload),
        'refresh_token': encryption.encode(SALT, refresh_payload),
        'user': user.pk
    }
    return result


# Create your views here.
class VerifyUsernameAPI(APIView):
    """
    Check the username is exist or not before register
    """

    @swagger_auto_schema(request_body=VerifyUserIn, responses={200: VerifyUserOut}, tags=['common'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[verify user] data: {request.data}')

        data_in = VerifyUserIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        result = dict(valid=False)
        try:
            User.objects.get(username=data_in.validated_data['username'])
        except ObjectDoesNotExist:
            result['valid'] = True

        data_out = VerifyUserOut(instance=result)
        logger.info(f'[verify user] success: {data_out.data}')
        return r200(data_out.data)


class RegisterAPI(APIView):
    """
    Register a new user
    """

    @swagger_auto_schema(request_body=RegisterIn, responses={200: RegisterOut}, tags=['common'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[register user] data: {request.data}')

        data_in = RegisterIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        try:
            user = User.objects.create_user(**data_in.validated_data)
        except Exception as e:
            logger.error(f'failed to create user: {e}')
            err = ERROR['REGISTER']
            err['data'] = str(e)
            raise APIException(err)

        result = generate_token(user)
        data_out = RegisterOut(instance=result)
        logger.info(f'[register user] id: {user} success: {data_out.data}')
        return r200(data_out.data)


class LoginAPI(APIView):
    """
    User login API
    """

    @swagger_auto_schema(request_body=LoginIn, responses={200: RegisterOut}, tags=['common'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[login] data: {request.data}')

        data_in = LoginIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        username = data_in.validated_data['username']
        password = data_in.validated_data['password']

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            logger.error(f'invalid username: {username}')
            err = ERROR['USER_NOT_FOUND']
            raise ValidationError(err)

        if not user.check_password(password):
            logger.error(f'invalid password')
            err = ERROR['INVALID_PASSWORD']
            raise AuthenticationFailed(err)

        result = generate_token(user)
        data_out = RegisterOut(instance=result)
        logger.info(f'[login] id: {user} success: {data_out.data}')
        return r200(data_out.data)


class RefreshJWT(APIView):
    """
    Using refresh token to get new token
    """

    @swagger_auto_schema(request_body=RefreshJWTIn, responses={200: RefreshJWTOut}, tags=['common'])
    def post(self, request, *args, **kwargs):
        logger.info(f'[refresh token] data: {request.data}')

        data_in = RefreshJWTIn(data=request.data)
        if not data_in.is_valid():
            logger.error(data_in.errors)
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)

        refresh_token = data_in.validated_data['refresh_token']
        try:
            payload = encryption.decode(SALT, refresh_token)
        except Exception as e:
            logger.error(f'failed to decode refresh token: {e}')
            err = ERROR['TOKEN_INVALID']
            err['data'] = str(e)
            raise ParseError(err)

        tm = timegm(datetime.utcnow().utctimetuple())
        if tm > payload['exp']:
            logger.info(f'refresh token expired')
            err = ERROR['TOKEN_EXP']
            err['data'] = 'fresh token'
            raise APIException(err)

        try:
            user = User.objects.get(id=payload['user_id'])
        except ObjectDoesNotExist:
            logger.error(f'invalid user ID: {payload["user_id"]}')
            err = ERROR['USER_NOT_FOUND']
            err['data'] = 'invalid user ID: ' + str(payload['user_id'])
            raise NotFound(err)

        token = generate_token(user)
        out = RefreshJWTOut(instance=token)
        logger.info(f'[refresh token] success: {out.data}')
        return r200(out.data)
