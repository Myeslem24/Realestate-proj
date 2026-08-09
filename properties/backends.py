from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get('phone_number')
        if not identifier or not password:
            return None

        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        if user is None:
            try:
                user = User.objects.get(phone_number=identifier)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

