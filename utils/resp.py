from typing import Dict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def r200(data: Dict) -> Response:
    return Response(data=data, status=status.HTTP_200_OK)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if 'code' in response.data:
            response.data['code'] = int(response.data['code'])
        else:
            response.data['code'] = exc.status_code
            response.data['message'] = exc.default_code
            response.data['data'] = response.data.pop('detail')
    else:
        data = {
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'internal error',
            'data': str(exc)
        }
        response = Response(data, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
