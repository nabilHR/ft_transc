from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(max_length=255,unique=True,verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=100,verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100,verbose_name=_("Last Name"))
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='usr_images/', null=True, blank=True)
    
    USERNAME_FIELD="email"

    # REQUIRED_FIELDS=["first_name","last_name"]

    objects= UserManager()

    def __str__(self):
        return f"{self.first_name}"
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        refresh=RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class OneTimePassword(models.Model):
    code=models.CharField(unique=True,max_length=6)
    user= models.ForeignKey(User,on_delete=models.CASCADE)

