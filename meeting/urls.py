from django.urls import path

from meeting.views import *

urlpatterns = [
    path('new/', NewMeetingAPI.as_view()),
    path('del/', DelMeetingAPI.as_view()),
    path('info/', MeetingInfoAPI.as_view()),
    path('list/', ListMeetingAPI.as_view()),
    path('join/', JoinMeetingAPI.as_view()),
    path('stop/', StopMeetingAPI.as_view()),
    path('start_share/', StartShareAPI.as_view()),
    path('stop_share/', StopShareAPI.as_view()),
]
