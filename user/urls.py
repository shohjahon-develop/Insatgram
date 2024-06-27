from .views import (CreateuserView, VerifyAPIView,LoginView,LoginRefreshView,LogOutView,
                    GetNewVerification,ChangeUserinformation,ForgotPasswordView,
                    ChangeUserPhotoView, ResetPasswordView)
from django.urls import path

urlpatterns = [
    path('signup',CreateuserView.as_view()),
    path('verify/',VerifyAPIView.as_view()),
    path('login/',LoginView.as_view()),
    path('login/refresh/',LoginRefreshView.as_view()),
    path('logout/',LogOutView.as_view()),
    path('new-verify/',GetNewVerification.as_view()),
    path('change-user/',ChangeUserinformation.as_view()),
    path('change-user-photo/',ChangeUserPhotoView.as_view()),
    path('forgot-password/',ForgotPasswordView.as_view()),
    path('reset-password/',ResetPasswordView)
]










































