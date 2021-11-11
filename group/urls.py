from django.urls import path

from group.views import *

urlpatterns = [
    path('start/', GroupStartAPI.as_view()),
    path('stop/', GroupStopAPI.as_view()),
    path('move_member/', MoveMemberAPI.as_view()),
    path('detail/', GroupDetailAPI.as_view()),
]
