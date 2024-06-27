from datetime import timedelta
from random import random
from uuid import uuid4

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.utils.datetime_safe import datetime

from shared.models import BaseModel
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.
ORDINARY_USER, MANAGER,ADMIN  = ("ordinary_user","manager","admin")
VIA_EMAIL , VIA_PHONE = ("via_email","via_phone")
NEW,CODE_VERIFIED,DONE,PHOTO_DONE = ("new","CODE_VERIFIED","PHOTO_DONE","done")





class User(AbstractUser,BaseModel):
    USER_ROLES = (
        (ORDINARY_USER,ORDINARY_USER),
        (MANAGER,MANAGER),
        (ADMIN,ADMIN)
    )

    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    AUTH_STATUS = (
        (NEW,NEW),
        (CODE_VERIFIED,CODE_VERIFIED),
        (PHOTO_DONE,PHOTO_DONE),
        (DONE,DONE)
    )

    user_roles = models.CharField(max_length=90,choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=90,choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=90,choices=AUTH_STATUS)
    email = models.EmailField(null=True,blank=True,unique=True)
    phone_number = models.CharField(max_length=90,null=True,blank=True,unique=True)
    photo = models.ImageField(upload_to='user_photos/',blank=True,null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['png','heic','jpg'])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def check_email(self):
        if self.email:
            oddiy_email = self.email.lower()
            self.email = oddiy_email

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randiant(0, 100) % 10) for _ in range(4)])

        UserConfirmation.objects.create(
            user=self.id,
            verify_type=verify_type,
            code=code
        )
        return code
    def check_username(self):
        if not self.username:
            temp_username = f'intagram{uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f'{temp_username}{random.randiant(0,9)}'
            self.username = temp_username

    def check_email(self):
        if self.email:
            normaline_email = self.email.lower()
            self.email = normaline_email


    def check_pass(self):
        if not self.password:
            temp_password = f'password{uuid4().__str__().split("-")[-1]}'
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access":str(refresh.access_token),
            "refresh_token":str(refresh)
        }

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()

    def save(self,*args,**kwargs):
        if not self.pk:
            self.clean()
        super(User,self).save(*args,**kwargs)




PHONE_EXPIRE = 2

EMAIL_EXPIRE = 5


class  UserConfirmation(models.Model):
    TYPE_CHOICES = (
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )

    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=40,choices=TYPE_CHOICES)
    user = models.ForeignKey('user.User',models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self,*args,**kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
            else:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
            super(UserConfirmation,self).save(*args,**kwargs)




class Post(models.Model):
    username = models.ForeignKey('user.User',models.CASCADE)
    like = models.IntegerField(default=0,blank=True,null=True)
    comment = models.TextField(blank=True,null=True)
    views = models.IntegerField(null=True,blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.email



























































































































































