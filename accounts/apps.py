from django.apps import AppConfig
from django.contrib.auth import login,get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.conf import settings


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self) -> None:
        User = get_user_model()

        NUMBER_FIELD = hasattr(User,'number')
        if NUMBER_FIELD:
            super().ready()
        else:
            raise FieldDoesNotExist('Need (number) as CharField On User Model')