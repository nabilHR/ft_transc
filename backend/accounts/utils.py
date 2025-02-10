import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings
from django.core.cache import cache
import pyotp
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64

def generateOtp():
    otp=""
    for i in range(6):
        otp += str(random.randint(1,9))
    return otp


def send_code_to_user(email,user_data):
    Subject="One time passcode for Email verification"
    otp_code=generateOtp()
    current_site="myAuth.com"
    email_body=f"Hello {user_data.first_name} thanks for signing up on {current_site} please {otp_code}"
    from_email=settings.DEFAULT_FROM_EMAIL
    OneTimePassword.objects.create(user=user_data,code=otp_code)
    d_email=EmailMessage(subject=Subject,body=email_body, from_email=from_email,to=[email])
    d_email.send(fail_silently=True)


def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body= data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()


#adding some shit to generate otp for 2fa and verify otp
def generate_otp_secret():
    return pyotp.random_base32()

def generate_otp_uri(user):
    return pyotp.totp.TOTP(user.otp_secret).provisioning_uri(user.email, issuer_name="Transcendence")

def verify_otp(user, otp):
    totp = pyotp.TOTP(user.otp_secret)
    return totp.verify(otp)


def generate_qr_code(otp_uri):
    qr = qrcode.QRCode(
        version=1,  
        error_correction=qrcode.constants.ERROR_CORRECT_L, 
        box_size=10,  
        border=4,  
    )


    qr.add_data(otp_uri)
    qr.make(fit=True)

    
    img = qr.make_image(fill_color="black", back_color="white")


    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    qr_data = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{qr_data}"


# AJE5IVCFSY6GY76B3OL3B77LX4VIWT33