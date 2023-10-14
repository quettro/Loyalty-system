import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from ...models import Reward

log = logging.getLogger(__name__)


@receiver(post_save, sender=Reward)
def reward_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_auto_update_client:
            count = instance.count

            if instance.is_type_debit:
                count = -count

            instance.client.a_rewards += count
            instance.client.save()

        log.info((
            f'[ {instance.get_type().label} ] Создана транзакция наград '
            f'клиента. Кол-во наград для зачисления/списания: '
            f'{instance.count}. Примечание: {instance.message} - '
            f'[ Дополнительные данные: {instance.__dict__} ]'
        ))
