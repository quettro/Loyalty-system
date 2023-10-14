from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import CustomToken


class BearerAuthentication(TokenAuthentication):
    model = CustomToken
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        model = self.get_model()

        token = model.objects.filter(key=key).select_related(
            'user',

            'user__partner',
            'user__partner__tariff',
            'user__partner__contract',
            'user__partner__contract__contract',

            'user__employee',
            'user__employee__partner',
            'user__employee__partner__contract',
            'user__employee__partner__contract__contract',
        ).first()

        if token is None:
            raise AuthenticationFailed(
                _('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(
                _('User inactive or deleted.'))

        if not token.user.is_partner and not token.user.is_employee:
            raise AuthenticationFailed(
                'Недостаточно информации для прохождения авторизации.')

        return (token.user, token)
