import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, APIException, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from meeting.models import Meeting
from poll.models import PollResult
from poll.serializers import *
from utils import cache
from utils.errors import ERROR
from utils.resp import r200

# Create your views here.
logger = logging.getLogger(__name__)


class PollListAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=PollListIn, responses={200: PollListOut}, tags=['poll'])
    def get(self, request, *args, **kwargs):
        """
        Get poll list in a meeting, only contains title
        """
        logger.info(f'[PollListAPI] user:{request.user.id} get poll list: {request.query_params}')
        data_in = PollListIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data['number']

        try:
            polls = Poll.objects.filter(
                Q(meeting__owner=request.user) | Q(
                    meeting__status__in=[Poll.Status.ONGOING.value, Poll.Status.DONE.value]),
                meeting__call_number=number)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        out = PollListOut(instance=polls, many=True)
        logger.info(f'[PollListAPI] success, poll size: {len(polls)}')
        return r200(out.data)


class PollDetailAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=PollIn, responses={200: PollDetailOut}, tags=['poll'])
    def get(self, request, *args, **kwargs):
        """
        Get a poll detail by poll ID
        Contain title, question, options
        """
        logger.info(f'[PollDetailAPI] user:{request.user.id} get poll detail: {request.query_params}')
        data_in = PollIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        tmp = {'title': poll.title, 'questions': [], 'meeting': poll.meeting, 'is_anonymous': poll.is_anonymous}
        qs = PollQuestion.objects.filter(poll=poll)
        for question in qs:
            options = PollOption.objects.filter(question=question)
            q_tmp = {'id': question.id, 'content': question.content, 'options': [], 'is_single': question.is_single}
            q_tmp['options'].extend([{'content': x.content, 'id': x.id} for x in options])
            tmp['questions'].append(q_tmp)

        out = PollDetailOut(instance=tmp)
        logger.info('[PollDetailAPI] success: {out.data}')
        return r200(out.data)


class PollNewAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollNewIn, tags=['poll'], responses={200: PollListOut})
    def post(self, request, *args, **kwargs):
        """
        Create a new poll
        """
        logger.info(f'[PollNewAPI] user:{request.user.id} create poll: {request.data}')

        data_in = PollNewIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        number = data_in.validated_data.pop('number')
        questions = data_in.validated_data.pop('questions')

        try:
            meeting = Meeting.objects.get(call_number=number, owner=request.user)
        except ObjectDoesNotExist:
            logger.error(f'user has no permission to create poll')
            err = ERROR['POLL_NOT_HOST']
            err['data'] = f'user: {request.user.id} not the owner'
            raise APIException(err)

        poll = None
        try:
            poll = Poll.objects.create(meeting=meeting, **data_in.validated_data)
            for q in questions:
                question, _ = PollQuestion.objects.get_or_create(content=q['content'], poll=poll,
                                                                 is_single=q['is_single'])
                for o in q['options']:
                    PollOption.objects.get_or_create(question=question, content=o['content'])
        except Exception as e:
            logger.error(f'failed to access database: {e}')
            if poll:
                poll.delete()
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        out = PollListOut(instance=poll)
        logger.info(f'[PollNewAPI] create poll success: {poll}')
        return r200(out.data)


class PollUpdateAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollUpdateIn, tags=['poll'])
    def post(self, request, *args, **kwargs):
        """
        Update a poll detail by poll ID
        """
        logger.info(f'[PollUpdateAPI] user:{request.user.id} update poll: {request.data}')

        data_in = PollUpdateIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']
        questions = data_in.validated_data['questions']

        try:
            poll = Poll.objects.get(pk=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)

        if poll.meeting.owner != request.user:
            logger.error(f'user has no permission to update poll')
            err = ERROR['POLL_NOT_HOST']
            err['data'] = f'user: {request.user.id} not the owner'
            raise PermissionDenied(err)

        try:
            poll.title = data_in.validated_data['title']
            poll.is_anonymous = data_in.validated_data['is_anonymous']
            poll.status = Poll.Status.NEW.value
            poll.share = Poll.ShareStatus.STOP.value
            poll.save(update_fields=['title', 'is_anonymous', 'status', 'share'])

            PollQuestion.objects.filter(poll=poll).delete()
            for q in questions:
                question, _ = PollQuestion.objects.get_or_create(content=q['content'], poll=poll,
                                                                 is_single=q['is_single'])
                for o in q['options']:
                    PollOption.objects.get_or_create(question=question, content=o['content'])
        except Exception as e:
            logger.error(f'failed to access database: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        logger.info(f'[PollUpdateAPI] success: {poll.id}')
        return r200({'status': 'success'})


class PollDeleteAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollIn, tags=['poll'])
    def post(self, request, *args, **kwargs):
        """
        Delete poll by poll ID
        """
        logger.info(f'[PollDeleteAPI] user:{request.user.id} delete poll: {request.data}')

        data_in = PollIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        if poll.status != Poll.Status.NEW.value:
            logger.warning(f'can not delete started or stopped poll: {poll_id}')
            err = ERROR['POLL_ALREADY_START']
            err['data'] = f'can not delete started or stopped poll: {poll_id}'
            raise ValidationError(err)

        if poll.meeting.owner != request.user:
            logger.error(f'user has no permission to update poll')
            err = ERROR['POLL_NOT_HOST']
            err['data'] = f'user: {request.user.id} not the owner'
            raise PermissionDenied(err)

        poll.delete()
        logger.info(f'[PollDeleteAPI] success: {poll_id}')
        return r200({'status': 'success'})


class PollResultAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=PollIn, tags=['poll'], responses={200: PollResultOut})
    def get(self, request, *args, **kwargs):
        """
        Get poll result summary by ID
        """
        logger.info(f'[PollResultAPI] user:{request.user.id} get poll result: {request.query_params}')

        data_in = PollIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
            poll_results = PollResult.objects.filter(poll=poll)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to access database: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        if poll.status == Poll.Status.NEW.value:
            logger.warning(f'poll not start: {poll_id}')
            err = ERROR['POLL_NOT_START']
            err['data'] = f'poll not start: {poll_id}'
            raise ValidationError(err)

        _qs = []
        data = {
            'title': poll.title,
            'is_anonymous': poll.is_anonymous,
            'status': poll.status,
            'voter_num': len(set(poll_results.values_list('voter_id', flat=True))),
            'questions': _qs
        }

        try:
            questions = PollQuestion.objects.filter(poll_id=poll_id)
            options = PollOption.objects.filter(question__in=questions)
        except Exception as e:
            logger.error(f'failed to get questions and options: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = f'failed to get questions and options: {e}'
            raise APIException(err)

        _tmp = {}
        for o in options:
            if _tmp.get(o.question.content, None) is None:
                _tmp[o.question.content] = {}
            if _tmp[o.question.content].get(o.content, None) is None:
                _tmp[o.question.content][o.content] = {'count': 0, 'voters': None}
            _tmp[o.question.content]['is_single'] = o.question.is_single

        _round = poll.round
        _is_anonymous = poll.is_anonymous
        for r in poll_results:
            if r.round != _round:
                continue
            _tmp[r.question.content][r.option.content]['count'] = _tmp[r.question.content][r.option.content].get(
                'count', 0) + 1
            if not _is_anonymous:
                if _tmp[r.question.content][r.option.content].get('voters', None) is None:
                    _tmp[r.question.content][r.option.content]['voters'] = []
                _tmp[r.question.content][r.option.content]['voters'].append(r.voter)
        for q_t, q_o in _tmp.items():
            answers = []
            is_single = q_o.pop('is_single')
            for o_c, o_a in q_o.items():
                _v = {'content': o_c}
                _v.update(o_a)
                answers.append(_v)
            _qs.append({'content': q_t, 'is_single': is_single, 'options': answers})

        out = PollResultOut(instance=data)
        logger.info(f'[PollResultAPI] success: {out.data}')
        return r200(out.data)


class PollStartAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollIn, tags=['poll'], responses={200: PollStartOut})
    def post(self, request, *args, **kwargs):
        """
        Start or re start a poll by poll ID
        """
        logger.info(f'[PollStartAPI] user:{request.user.id} start poll: {request.data}')

        data_in = PollIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        lock_name = f'new-pull-lock-{poll.meeting.call_number}'
        _lock = None
        try:
            _lock = cache.acquire_lock_with_timeout(
                lock_name, poll.meeting.call_number, acquire_timeout=10, lock_timeout=10)
        except Exception as e:
            logger.error(f'failed to lock room: {e}')
            err = ERROR['INTERNAL']
            err['data'] = str(e)
            raise APIException(err)

        if _lock is None:
            err = ERROR['POLL_ALREADY_START']
            err['data'] = f'poll already start: {poll_id}'
            raise APIException(err)

        if poll.status == Poll.Status.ONGOING.value:
            logger.warning(f'poll already start: {poll_id}')
            err = ERROR['POLL_ALREADY_START']
            err['data'] = f'poll already start: {poll_id}'
            cache.release_lock(lock_name, _lock)
            raise APIException(err)

        try:
            polls = Poll.objects.filter(meeting=poll.meeting)
        except Exception as e:
            logger.error(f'failed to access database: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            cache.release_lock(lock_name, _lock)
            raise APIException(err)

        # One meeting only start a poll
        for _poll in polls:
            if _poll.status == Poll.Status.ONGOING.value:
                logger.warning(f'already start poll {_poll.id} in meeting {_poll.meeting.call_number}')
                err = ERROR['POLL_EXIST']
                err['data'] = f'already start poll {_poll.id} in meeting {_poll.meeting.call_number}'
                cache.release_lock(lock_name, _lock)
                raise ValidationError(err)

        try:
            Poll.objects.filter(id=poll.id).update(
                status=Poll.Status.ONGOING.value,
                share=Poll.ShareStatus.STOP.value,
                round=poll.round + 1
            )
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
        finally:
            cache.release_lock(lock_name, _lock)

        out = PollStartOut(instance=poll)
        logger.info(f'[PollStartAPI] success: {out.data}')
        return r200(out.data)


class PollStopAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollIn, tags=['poll'], responses={200: PollStartOut})
    def post(self, request, *args, **kwargs):
        """
        Stop poll by poll ID
        """
        logger.info(f'[PollStopAPI] user:{request.user.id} stop poll: {request.data}')

        data_in = PollIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id, status=Poll.Status.ONGOING.value)
        except ObjectDoesNotExist:
            logger.error(f'not fount ongoing poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'not fount ongoing poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        if poll.meeting.owner != request.user:
            logger.error(f'user has no permission to stop poll')
            err = ERROR['POLL_NOT_HOST']
            err['data'] = f'user: {request.user.id} not the owner'
            raise PermissionDenied(err)

        poll.status = Poll.Status.DONE.value
        poll.save(update_fields=['status'])
        out = PollStartOut(instance=poll)
        logger.info(f'[PollStopAPI] success: {out.data}')
        return r200(out.data)


class PollCommitAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=PollCommitIn, tags=['poll'], responses={200: PollCommitOut})
    def post(self, request, *args, **kwargs):
        """
        Commit my answer
        """
        logger.info(f'[PollCommitAPI] user:{request.user.id} commit poll: {request.data}')

        data_in = PollCommitIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['poll_id']

        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'not found ongoing poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'not fount ongoing poll ID: {poll_id}'
            raise NotFound(err)
        if poll.status == Poll.Status.DONE.value:
            logger.warning(f'poll is over: {poll_id}')
            err = ERROR['POLL_ALREADY_DONE']
            err['data'] = f'poll is over: {poll_id}'
            raise ValidationError(err)

        if poll.status == Poll.Status.NEW.value:
            logger.warning(f'poll not start: {poll_id}')
            err = ERROR['POLL_NOT_START']
            err['data'] = f'poll not start: {poll_id}'
            raise APIException(err)

        for q in data_in.validated_data['questions']:
            for o_id in q['options']:
                PollResult.objects.create(poll_id=poll_id, question_id=q['id'], option_id=o_id['id'],
                                          voter=request.user, round=poll.round)

        data = {'poll_id': poll_id, 'round': poll.round}
        out = PollCommitOut(instance=data)
        logger.info(f'[PollCommitAPI] success: {out.data}')
        return r200(out.data)


class PollAnswerAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(query_serializer=PollIn, tags=['poll'], responses={200: PollAnswerOut})
    def get(self, request, *args, **kwargs):
        """
        Get my answer
        """
        logger.info(f'[PollAnswerAPI] user:{request.user.id} get his answer: {request.query_params}')

        data_in = PollIn(data=request.query_params)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
            poll_results = PollResult.objects.filter(poll_id=poll_id, voter=request.user,
                                                     round=poll.round)
        except Exception as e:
            logger.error(f'failed to access database: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        user_options = [x.option.id for x in poll_results]
        tmp = {'title': poll.title, 'questions': []}
        qs = PollQuestion.objects.filter(poll=poll)
        for question in qs:
            options = PollOption.objects.filter(question=question)
            q_tmp = {'content': question.content, 'options': [], 'is_single': question.is_single}
            q_tmp['options'].extend([{'content': x.content, 'select': x.id in user_options} for x in options])
            tmp['questions'].append(q_tmp)

        out = PollAnswerOut(instance=tmp)
        logger.info(f'[PollAnswerAPI] success: {out.data}')
        return r200(out.data)


class ChangeShareStatusAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=ChangeShareStatusIn, tags=['poll'], responses={200: PollListOut})
    def post(self, request, *args, **kwargs):
        """
        Change poll share status
        """
        logger.info(f'[ChangeShareStatusAPI] user:{request.user.id} change poll result share status: {request.data}')

        data_in = ChangeShareStatusIn(data=request.data)
        if not data_in.is_valid():
            logger.error(f'invalid parameter: {data_in.errors}')
            err = ERROR['INPUT']
            err['data'] = data_in.errors
            raise ValidationError(err)
        poll_id = data_in.validated_data['id']

        try:
            poll = Poll.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            logger.error(f'invalid poll ID: {poll_id}')
            err = ERROR['POLL_NOT_FOUND']
            err['data'] = f'invalid poll ID: {poll_id}'
            raise NotFound(err)
        except Exception as e:
            logger.error(f'failed to get poll list: {e}')
            err = ERROR['GET_POLL_FAILED']
            err['data'] = str(e)
            raise APIException(err)

        poll.share = data_in.validated_data['share']
        try:
            poll.save(update_fields=['share'])
        except Exception as e:
            logger.error(f'failed to update poll share status: {e}')
            err = ERROR['POLL_INFO_DATABASE']
            err['data'] = str(e)
            raise APIException(err)

        out = PollListOut(instance=poll)
        logger.info(f'[ChangeShareStatusAPI] success: {out.data}')
        return r200(out.data)
