import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from ...models import Reward, Stamp

log = logging.getLogger(__name__)


@receiver(post_save, sender=Stamp)
def stamp_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_auto_update_client:
            client = instance.client

            if instance.is_type_debit:
                client.a_stamps -= instance.count

            elif instance.is_type_credit:
                count = instance.count + client.a_stamps
                rewards = count // client.wallet.stamps

                client.a_stamps = count % client.wallet.stamps
                client.c_stamps += instance.count

                if rewards > 0:
                    client.a_rewards += rewards

                    Reward(
                        is_auto_update_client=False,
                        client=client,
                        type=Reward.Type.CREDIT,
                        count=rewards,
                        message=(
                            'Зачисление наград в связи с заполнением всех '
                            'штампов.'
                        )
                    ).save()

            client.save()

        log.info((
            f'[ {instance.get_type().label} ] Создана транзакция штампов '
            f'клиента. Кол-во штампов для зачисления/списания: '
            f'{instance.count}. Примечание: {instance.message} - '
            f'[ Дополнительные данные: {instance.__dict__} ]'
        ))
