from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from Shop.settings import DRF_TOKEN_LIFE_TIME


class TokenWithLifeTimeAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key=key)
        if (timezone.now() - token.created).seconds > DRF_TOKEN_LIFE_TIME:
            token.delete()
            raise exceptions.AuthenticationFailed('Token is expired. Get new one.')
        return user, token
