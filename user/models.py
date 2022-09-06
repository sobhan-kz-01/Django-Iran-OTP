from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from datetime import date, datetime
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):

    number = models.PositiveBigIntegerField(verbose_name='شماره همراه',null=True,unique=True)

    def __str__(self):
        return str(self.number)
