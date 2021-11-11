from django.urls import path

from poll.views import *

urlpatterns = [
    path('list/', PollListAPI.as_view()),
    path('detail/', PollDetailAPI.as_view()),
    path('del/', PollDeleteAPI.as_view()),
    path('result/', PollResultAPI.as_view()),
    path('new/', PollNewAPI.as_view()),
    path('update/', PollUpdateAPI.as_view()),
    path('start/', PollStartAPI.as_view()),
    path('stop/', PollStopAPI.as_view()),
    path('commit/', PollCommitAPI.as_view()),
    path('answer/', PollAnswerAPI.as_view()),
    path('share/', ChangeShareStatusAPI.as_view()),
]
