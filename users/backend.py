# accounts/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, phone=None, **kwargs):
        # поддержим и username, и phone
        phone_value = phone or username
        if not phone_value or not password:
            return None

        try:
            user = User.objects.get(phone=phone_value)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
