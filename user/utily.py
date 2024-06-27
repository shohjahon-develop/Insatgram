import re
import threading
import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from twilio.rest import Client
from rest_framework.exceptions import ValidationError





email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
phone_regex = re.compile(r"(\+[0-9]+s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+")
user_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")



def check_email_phone(email_phone_number):


    if (re.fullmatch(email_phone_number,email_regex)):
        email_phone_number = 'email'
    elif (re.fullmatch(email_phone_number,phone_regex)):
        email_phone_number = 'phone'
    else:
        data = {
            "status":False,
            "message":"Email yoki telefon raqam xato kiritilgan"
        }
        raise ValidationError(data)
    return email_phone_number

class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == 'html':
            email.content_subtype == 'hmtl'
        EmailThread(email).start()

def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code":code}
    )

    Email.send_email(
        {
            "subject":"Ro'yxatdan o'tish",
            "to_email":email,
            "body":html_content,
            "content_type":"html"
        }
    )


def send_phone_number(phone,code):
    account_sid = config("account_sid")
    auth_token = config("auth_token")

    client = Client(account_sid,auth_token)
    client.messages.create(
        body=f"Sizning akkountga kirish kodingiz:{code}",
        from_="+998930034867",
        to=f"{phone}"
    )

def check_user_type(user_input):
    if re.fullmatch(email_regex,user_input):
        user_type = 'email'
    elif re.fullmatch(phone_regex,user_input):
        user_type = 'phone'
    elif re.fullmatch(user_regex,user_input):
        user_type = 'username'
    else:
        data = {
            "success":False,
            "message":"Email, username yoki phone number kiritish kerak"
        }
        raise ValidationError(data)
    return user_type

def check_email_or_phone(email_phone):
    phone_number = phonenumbers.perse(email_phone)

    if re.fullmatch(email_regex,email_phone):
        email_or_phone = "email"
    elif phonenumbers.is_valid_number(phone_number):
        email_or_phone = "phone"
    else:
        data = {
            "success":False,
            "message":"Email yoki telefon raqam xato"
        }
        raise ValidationError(data)
    return email_or_phone


# def send_email(email, code):
#     return































































































































