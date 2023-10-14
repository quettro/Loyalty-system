from config.celery import app
from django.db.models import F
from django.utils import timezone

from ..models import Bonus, Client, Trigger
from .notifications import send_push_notifications


@app.task
def triggers():
    launch_at = timezone.now().replace(minute=0, second=0, microsecond=0)
    triggers = Trigger.objects.wallet_not_deleted().filter(launch_at=launch_at)

    for trigger in triggers:
        clients = None

        """
        Если активирован чекбокс "Начислить баллы?", то начинаем начислять
        баллы активным клиентам.
        """
        if trigger.is_add_bonuses and trigger.bonuses > 0:
            if trigger.audience is None:
                clients = trigger.wallet.clients.not_deleted()
            else:
                clients = trigger.audience.get_clients()

            clients = clients.select_related('wallet')
            clients.update(balance=F('balance') + trigger.bonuses)

            Bonus.objects.bulk_create([
                Bonus(
                    is_auto_update_client=False,
                    client=client,
                    type=Bonus.Type.CREDIT,
                    count=trigger.bonuses,
                    message=(
                        'Зачисление бонусов в связи с событием '
                        f'"{trigger.name}".'
                    )
                ) for client in clients
            ])

        """
        Если активирован чекбокс "Отправить пуш уведомления?", то начинаем
        рассылку пуш уведомлений.
        """
        if trigger.is_send_push_notifications:
            """
            Делаем запрос в базу данных только в том случае, если выше не
            доставали клиентов из базы данных.
            """
            if clients is None:
                if trigger.audience is None:
                    clients = trigger.wallet.clients.not_deleted()
                else:
                    clients = trigger.audience.get_clients()

                clients = clients.select_related('wallet')

            ids = []

            for client in clients:
                client.override_pkpass(trigger.message_for_push_notifications)
                ids.append(client.id)

            Client.objects.bulk_update(clients, ['pkpass'])
            send_push_notifications.apply_async(args=[ids], countdown=15)

        """
        Если активирован чекбокс "Повторять событие каждый год?", то
        заменяем в дате запуска значение "Год" на +1 и сохраняем запись.
        """
        if trigger.is_repeat_every_year:
            year = trigger.launch_at.year
            trigger.launch_at = trigger.launch_at.replace(year=(year + 1))
            trigger.save()
