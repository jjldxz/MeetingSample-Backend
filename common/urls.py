from django.urls import path

from common.views import VerifyUsernameAPI, RegisterAPI, LoginAPI, RefreshJWT

urlpatterns = [
    path('verify_username/', VerifyUsernameAPI.as_view()),
    path('register/', RegisterAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('refresh_token/', RefreshJWT.as_view()),
]
