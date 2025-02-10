from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def email_validator(self,email):
        try:
            validate_email(email)
        except:
            raise ValueError(_("Your mail is not valid ,PLEASE Enter a valid one *-*"))

    def create_user(self,email,first_name,last_name,password = None,**extra_fields):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("an email address is required"))
        if not first_name:
            raise ValueError(_("first name is required"))
        user=self.model(email=email,first_name=first_name,last_name=last_name,**extra_fields)
        if password:
            user.set_password(password)
        else: 
            user.set_unusable_password()
        user.save(using=self._db)
        return user