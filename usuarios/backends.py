from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import MultipleObjectsReturned
from .models import CustomUser

class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return None