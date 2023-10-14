import logging

from config.celery import app
from django.conf import settings
from libraries.android import WalletPasses
from libraries.apns import APNsPusher

from ..models import Client, Push

log = logging.getLogger(__name__)


@app.task
def send_push_notifications(clients, push_id=None):
    """
    Отправка PUSH уведомлений на устройства Android и iOS.
    """
    clients = Client.objects.filter(id__in=clients).select_related(
        'wallet', 'wallet__cert'
    ).prefetch_related('registrations')

    push = None
    content = {'Android': [], 'iOS': []}

    if type(push_id) == int:
        push = Push.objects.filter(id=push_id).first()

        if type(push) == Push:
            push.status = Push.Status.PROCESSING
            push.save()

    for client in clients:
        if type(push) == Push:
            client.override_pkpass(push.message)
            client.save()

        cert = client.wallet.cert

        tokens = list(
            client.registrations.filter(
                os_family__icontains='Android'
            ).values_list('push_token', flat=True)
        )

        if tokens:
            """
            Отправка PUSH уведомлений на устройства Android.
            """
            content['Android'].append(tokens)

            message = 'Отправка PUSH уведомлений на Android устройства: {}.'
            log.info(message.format(tokens))

            try:
                walletpasses = WalletPasses()
                walletpasses.push(cert.p12_pass_type_identifier, tokens)
            except Exception as e:
                log.error(e, exc_info=True)

        tokens = list(
            client.registrations.filter(
                os_family__icontains='iOS'
            ).values_list('push_token', flat=True)
        )

        if tokens:
            """
            Отправка PUSH уведомлений на устройства iOS.
            """
            content['iOS'].append(tokens)

            message = 'Отправка PUSH уведомлений на iOS устройства: {}.'
            log.info(message.format(tokens))

            apns = APNsPusher(
                apns_key_id=cert.p8_key,
                apns_key_path=cert.p8_cert.path,
                team_id=cert.p12_team_identifier,
                bundle_id=cert.p12_pass_type_identifier
            )

            for token in tokens:
                try:
                    apns.push('Title', 'Body', token, settings.DEBUG)
                except Exception as e:
                    log.error(e, exc_info=True)

    if type(push) == Push:
        push.status = Push.Status.COMPLETED
        push.save()

    return content
