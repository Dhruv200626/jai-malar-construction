"""
Custom authentication backend — allows login with email OR username
"""
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate using email or username.
    Falls back to Django's default ModelBackend behaviour.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            # Accept both email and plain username
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except User.DoesNotExist:
            # Run default hasher to prevent timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Edge case: return None if somehow duplicates exist
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
