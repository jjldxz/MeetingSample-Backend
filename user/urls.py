from django.urls import path

from user.views import UserInfoAPI, UpdateInfoAPI, ChangePwdAPI

urlpatterns = [
    path('info/', UserInfoAPI.as_view()),
    path('change_pwd/', ChangePwdAPI.as_view()),
    path('update_info/', UpdateInfoAPI.as_view()),
]
