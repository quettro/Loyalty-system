import datetime
import logging
import re

from apps.base.models import Client
from apps.base.tasks import send_push_notifications
from django.db.models import Max
from django.http import HttpResponse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from user_agents import parse

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

log = logging.getLogger(__name__)


class AuthorizationMixin:
    client = None

    def is_authorization(self, request, *args, **kwargs):
        pattern = r'^.*?Pass\s(.*?)$'
        authorization = request.META.get('HTTP_AUTHORIZATION', '')
        authorization = re.match(pattern, authorization)
        authentication_token = authorization.group(1)

        log.info((
            'Авторизация устройства. Headers: {}. Meta: {}. Token: {}. - {}'
        ).format(
            request.headers, request.META, authentication_token, kwargs
        ))

        if not authorization:
            raise NotAuthenticated()

        self.client = Client.objects.not_deleted().filter(
            authentication_token=authentication_token
        ).select_related(
            'wallet'
        ).prefetch_related(
            'registrations'
        ).first()

        if not self.client:
            raise NotFound()

        if str(self.client.numbers) != str(kwargs.get('serial_number')):
            raise NotAuthenticated()


class RegisterPassViewSet(AuthorizationMixin, APIView):
    permission_classes = []
    http_method_names = ('post', 'delete',)

    def post(self, request, *args, **kwargs):
        self.is_authorization(request, *args, **kwargs)

        device_library_id = kwargs.get('device_library_id')
        push_token = request.data.get('pushToken')

        instance = self.client.registrations.filter(
            device_library_id=device_library_id
        ).first()

        if not instance:
            _status = status.HTTP_201_CREATED

            user_agent = request.META.get('HTTP_USER_AGENT')
            user_agent = parse(user_agent)

            self.client.registrations.create(
                device_library_id=device_library_id,
                push_token=push_token,
                os_family=user_agent.os.family,
                os_version=user_agent.os.version_string,
                device_family=user_agent.device.family,
                device_brand=user_agent.device.brand,
                device_model=user_agent.device.model
            )
        else:
            _status = status.HTTP_200_OK

            if instance.push_token != push_token:
                instance.push_token = push_token
                instance.save()

        message = self.client.wallet.backend['activation_message']
        self.client.override_pkpass(message)
        self.client.save()

        send_push_notifications.delay([self.client.id])

        log.info(
            (
                'Карта: {}, активирована на устройстве: {}. '
                'Полученные данные: {}, {}. Данные карты: {}'
            ).format(
                self.client.numbers, device_library_id, request.data,
                kwargs, self.client.__dict__
            )
        )

        return Response(status=_status)

    def delete(self, request, *args, **kwargs):
        self.is_authorization(request, *args, **kwargs)

        device_library_id = kwargs.get('device_library_id')

        self.client.registrations.filter(
            device_library_id=device_library_id
        ).delete()

        if self.client.registrations.count() <= 0:
            self.client.softdelete()

        log.info(
            (
                'Карта: {}, удалена с устройства: {}. Полученные данные: '
                '{}, {}. Данные карты: {}'
            ).format(
                self.client.numbers, device_library_id, request.data,
                kwargs, self.client.__dict__
            )
        )

        return Response(status=status.HTTP_200_OK)


class RegistrationsViewSet(APIView):
    permission_classes = []
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        clients = Client.objects.not_deleted().filter(
            registrations__device_library_id=kwargs.get(
                'device_library_id'
            )
        )

        if clients.count() <= 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if 'passesUpdatedSince' in request.GET:
            clients = clients.filter(
                updated_at__gt=make_aware(
                    datetime.datetime.strptime(
                        request.GET.get('passesUpdatedSince'), DATETIME_FORMAT
                    )
                )
            )

        if clients:
            last_updated = clients.aggregate(
                Max('updated_at')
            )['updated_at__max']

            numbers = [
                c.numbers for c in clients.filter(
                    updated_at=last_updated
                )
            ]

            last_updated = last_updated.strftime(DATETIME_FORMAT)
            context = {'lastUpdated': last_updated, 'serialNumbers': numbers}
            return Response(context)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LatestVersionViewSet(AuthorizationMixin, APIView):
    permission_classes = []
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        self.is_authorization(request, *args, **kwargs)

        ct = 'application/vnd.apple.pkpass'

        response = HttpResponse(self.client.pkpass.read(), content_type=ct)
        response['Content-Disposition'] = 'attachment; filename=pkpass.pkpass'

        return response


class LogViewSet(APIView):
    permission_classes = []
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        log.info((
            'Получены ошибки, отправленные с телефона (.pkpass): {}. '
            'request.META: {}'
        ).format(
            request.data,
            request.META
        ))


class TestViewSet(APIView):
    permission_classes = []
    http_method_names = ('get',)

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')

        if not token:
            return HttpResponse('[ Token ] Not found.')

        client = Client.objects.not_deleted().filter(
            authentication_token=token
        ).first()

        if not client:
            return HttpResponse('[ Client ] Not found.')

        ct = 'application/vnd.apple.pkpass'

        response = HttpResponse(client.pkpass.read(), content_type=ct)
        response['Content-Disposition'] = 'attachment; filename=pkpass.pkpass'

        return response
