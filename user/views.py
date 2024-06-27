from django.core.exceptions import ObjectDoesNotExist
from django.db.migrations import serializer
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,UpdateAPIView
from rest_framework.exceptions import ValidationError,NotFound
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utily import send_email, send_phone_number, check_email_or_phone
from django.utils.dateformat import datetime
from .serializers import SignUpSerializer, RestPasswordSerializer
from .models import User,NEW,DONE ,PHOTO_DONE,CODE_VERIFIED,VIA_PHONE,VIA_EMAIL
from rest_framework import  permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,ResetPasswordView
from .serializers import (ChangeUserinformation,SignUpSerializer,ChangeUserPhotoSerializer,LoginSerializer,RestPasswordSerializer,LoginRefreshSerializer,LogoutSerializer, ForgotPasswordSerilaizer)

# Create your views here.




class CreateuserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

class VerifyAPIView(APIView):
    permissions_classes = (IsAuthenticated,)

    def post(self,request,*args,**kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user,code)

        return Response(
            data = {
                "success":True,
                'auth_status':user.auth_status,
                "access":user.token()['access'],
                "refresh":user.token()['refresh_token']
            }
        )

@staticmethod
def check_verify(user,code):
    verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(),code=code,is_confired=False)

    if not verifies.exists():
        data = {
            "success":False,
            "message":'Tasdiqlash kodingiz xato yoki eskirgan'
        }
        raise ValidationError(data)
    else:
        verifies.update(is_confirmed=True)
    if user.auth_status == NEW:
        user.auth_status == CODE_VERIFIED
        user.save()
    return True



class GetNewVerification(APIView):

    def get(self,request,*args,**kwargs):
        user = self.request.user
        self.check_verification(user)
        if user._auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email,code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_phone_number(user.phone_number,code)
        else:
            data = {
                "success":False,
                "message":"Email yoki telefon raqami xato"
            }
            raise ValidationError(data)


        return Response(
            {
                "success":True,
                "message":"Tasdiqlash kodi qayta yuborildi"
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.create_verify_code(expiration_time__gte=datetime.now(),is_confirmed=False)
        if verifies.exists():
            data = {
                "message":"Kodingiz hali ishlatish uchun yaroqli.Biroz kuting "

            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes(IsAuthenticated,)
    serializer_class = ChangeUserinformation
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user

    def update(self,request,*args,**kwargs):
        super(ChangeUserInformationView,self).update(request,*args,**kwargs)
        data = {
            "success":True,
            "message":"user muvafaqiyatli o'zgartirildi",
            'auth_status':self.request.user.auth_status
        }
        return Response(data,status=200)

    def partial_update(self,request,*args,**kwargs):
        super(ChangeUserInformationView,self).partial_update(request,*args,**kwargs)
        data = {
            "success":True,
            'message':"user muvaffaqiyatli o'zgartirildi",
            "auth_status":self.request.user.auth_status
        }
        return Response(data,status=200)


class ChangeUserPhotoView(APIView):
    permission_classes = [IsAuthenticated,]

    def put(self,request,*args,**kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            serializer.update(user,serializer.validated_data)
            return Response({
                "success":True,
                "message":"Rasm muvaffaqiyatli o'zgartirildi"
            }, status=200)
        return Response(
            serializer.errors,status=400
        )

class LoginView(TokenObtainPairView):
    serializer_class = LogoutSerializer

class LoginRefreshView(TokenRefreshView):
    serilaizer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serilaizer_class = LogoutSerializer
    permission_classes = [IsAuthenticated,]

    def post(self,request,*args,**kwargs):
        serializer = self.serilaizer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success":True,
                "message":"Siz logout bo'ldingiz"
            }
            return Response(data,status=205)
        except TokenError:
            return Response(status=400)


class LogoutSerializer(serializer.Serializer):
    refresh = serializer.CharField()

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny,]
    serializer_class = ForgotPasswordSerilaizer

    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_phone = serializer.validated_data.get("email_or_phone")
        user = serializer.validated_data.get("user")
        if check_email_or_phone(email_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_phone_number(email_phone,code)
        if check_email_or_phone(email_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_phone_number(email_phone,code)

        return Response({
            "success":True,
            "message":"Tasdiqlash kodi muvofaqiyatli yuborildi",
            "access":user.token()['access'],
            "refresh":user.token()['refresh_token'],
            "user_status":user.auth_status
        },status=200)





class ResetPasswordView(UpdateAPIView):
    serializer_class = RestPasswordSerializer
    permission_classes = [IsAuthenticated,]
    http_method_names = ['patch','put']

    def get_object(self):
        return self.request.user

    def update(self,request,*args,**kwargs):
        response = super(ResetPasswordView,self).update(request,*args,**kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User topilmadi")
        return Response(
            {
                "success":True,
                "message":"parolingiz movafaqiyatli o'zgartirildi",
                "access":user.token()['access'],
                "refresh":user.token()['refresh_token']
            }
        )























































































































