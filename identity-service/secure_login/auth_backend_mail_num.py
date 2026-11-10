from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import CustomUser


class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        user = CustomUser.objects.filter(
            Q(email__iexact=username) | Q(phone_number=username)
        ).first()
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None