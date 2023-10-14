from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Client, Reward, Wallet


@receiver(post_save, sender=Wallet)
def wallet_post_save(sender, instance, created, *args, **kwargs):
    """
    Если поле `stamps` у карты было обновлено в меньшую сторону, то получаем
    список клиентов которым необходимо зачислить награды и обновить поле
    с активными штампами.
    """
    if not created:
        if instance.stamps != instance._stamps:
            if instance._stamps > instance.stamps:
                clients = instance.clients.filter(
                    a_stamps__gte=instance.stamps)

                if clients:
                    t_rewards = []

                    for client in clients:
                        _stamps = client.a_stamps % instance.stamps
                        _rewards = client.a_stamps // instance.stamps

                        client.a_stamps = _stamps
                        client.a_rewards += _rewards

                        t_rewards.append(
                            Reward(
                                is_auto_update_client=False,
                                client=client,
                                type=Reward.Type.CREDIT,
                                count=_rewards,
                                message=(
                                    '[ Кол-во штампов для получения награды '
                                    'было обновлено ]. Зачисление наград в '
                                    'связи с заполнением всех штампов.'
                                )
                            )
                        )

                    """
                    У всех клиентов обновляем поля `a_stamps` и `a_rewards`.
                    """
                    Client.objects.bulk_update(
                        clients, [
                            'a_stamps', 'a_rewards'
                        ]
                    )

                    """
                    Массово создаем N записей в базе данных с транзакциями
                    наград.
                    """
                    Reward.objects.bulk_create(t_rewards)
