from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied
from django.core.validators import FileExtensionValidator

from .models import User, UserConfirmation, NEW, VIA_PHONE, VIA_EMAIL, DONE, PHOTO_DONE, CODE_VERIFIED
from rest_framework import exceptions
from django.db.models import Q
# from rest_framework_simplejwt.serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .utily import check_email_phone, check_user_type, send_email


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)


    class Meta:
        model=User
        fields = (
            "id",
            "auth_type",
            "auth_status"
        )

    extra_kwargs = {
        'auth_type' :{
            'read_only':True, 'required':False
        },
        'auth_status':{
            'read_only':True,'required':False
        }
    }

    def create(self,validated_data):
        user = super(SignUpSerializer,self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email,code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number,code)

        user.save()
        return user

    def validate(self,data):
        super(SignUpSerializer,self).validate(data)
        data = self.auth_validate(data)
        return data


    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_phone(user_input)
        if input_type == 'email':
            data = {
                "email":user_input,
                "auth_type":VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                "phone":user_input,
                "auth_type":VIA_PHONE
            }
        else:
            data = {
                'success':False,
                "message":"You must send email or phone number"
            }
            raise ValidationError(data)
        return data

    def validate_email_phone_number(self,value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success":False,
                "message":"Bu email allaqchon ma'lumotlar bazasida bor "

            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                "success":False,
                "message":"Bu telefon raqami allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)

        return value

    def to_representation(self,intance):
        data = super(SignUpSerializer,self).to_representation(intance)
        data.update(intance.token())

        return data




class ChangeUserinformation(serializers.Serializer):
    first_name  = serializers.CharField(write_only=True,required=True)
    last_name = serializers.CharField(write_only=True,required=True)
    username = serializers.CharField(write_only=True,required=True)
    password = serializers.CharField(write_only=True,required=True)
    confirm_password = serializers.CharField(write_only = True,required=True)



    def validate(self, data):
        password = data.get('password',None)
        confirm_password = data.get('confirm_password',None)
        if password != confirm_password:
            raise ValidationError({
                "message":"Parolingiz va tastiqlash parolingiz bir"
                          "biriga teng emas"
            })
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self,data):
        username = data.get("username",None)

        if len(username)<5 or len(username)>30:
            raise ValidationError({
                "message": "username 5ta belgidan kichik  va 30 ta belgidan kichik bo'lishi kerak"
            })


        if username.isdigit():
            raise ValidationError({
                "message":"Username faqat raqamlardan iborat"
            })
        return data

    def update(self,instance,validated_data):
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.password = validated_data.get('password',instance.password)
        instance.username = validated_data.get('username',instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=[
        'jpg','jpeg','png','heic','heif'
    ])])

    def update(self,instance,validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()

        return instance



class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self,*args,**kwargs):
        super(LoginSerializer,self).__init__(*args,**kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False,read_only=True)


    def auth_validate(self,data):
        user_input = data.get('userinput')
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone__iexact=user_input)
            username = user.username
        else:
            data = {
                'success':False,
                "message":"Siz email ,username yoki telefon raqam jo'natishingiz kerak"

            }

            raise ValidationError(data)

        authentication_kwargs = {
            self.username_fields:username,
            'password':data['password']
        }

        current_user = User.objects.filter(username_iexact=username).first()

        if (current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]):
            raise ValidationError(
                {
                    "success":False,
                    "message":"Siz ro'yxatdan to'liq o'tkansiz"
                }
            )


    def validate(self,data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE ,PHOTO_DONE]:
            raise PermissionDenied('Siz login qila olmaysiz , Ruxsat yoq')
        data = self.user_token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name

        return data

    def get_user(self,**kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "status":False,
                    "message":"Hech qanday aktiv akkaountlar topilmadi."
                }
            )
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self,attrs):
        email_or_phone = attrs.get('email_or_phone',None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success":False,
                    "message":"Email yoki telefon raqami kiritilishi shart"
                }
            )
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User not found")
        attrs['user'] = user.first()
        return attrs

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ForgotPasswordSerilaizer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True,required=True)

    def validate(self,attrs):
        email_or_phone = attrs.get('email_or_phone',None)
        if email_or_phone is None:
            raise ValidationError({
                'success':False,
                "message":"Email yoki Telefon raqam kiriting"
            })
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User not Found")
        attrs['user'] = user.first()
        return attrs


class RestPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True,write_only=True)
    confirm_password = serializers.CharField(min_length=8,required=True,write_only=True)


    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

    def validate(self,data):
        password = data.get('password', None)
        confirm_password = data.get('password',None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "success":False,
                    "message":"Parolni to'g'ri takrorlang!"

                }
            )
        if password:
            validate_password(password)
        return data

    def update(self,instance,validate_data):
        password = validate_data.pop("password")
        instance.set_password(password)
        return super(RestPasswordSerializer,self).update(instance,validate_data)


