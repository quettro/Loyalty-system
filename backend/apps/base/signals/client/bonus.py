import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from ...models import Bonus

log = logging.getLogger(__name__)


@receiver(post_save, sender=Bonus)
def bonus_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_auto_update_client:
            client = instance.client

            if instance.is_type_credit:
                client.balance += instance.count

            elif instance.is_type_debit:
                client.balance -= instance.count

                if instance.transaction is not None:
                    bonuses_to_rub = instance.count * client.wallet.conversion
                    amount = instance.transaction.amount - bonuses_to_rub
                    bonuses = amount / client.wallet.conversion
                    bonuses = bonuses / 100 * instance.transaction.percent

                    if bonuses > 0:
                        client.balance += bonuses

                        client.t_bonuses.create(
                            is_auto_update_client=False,
                            transaction=instance.transaction,
                            type=Bonus.Type.CREDIT,
                            count=bonuses,
                            message=(
                                f'Автоматическое зачисление баллов. Кэшбэк '
                                f'клиента: {instance.transaction.percent}%. '
                                f'Сумма покупок с учетом вычета баллов: '
                                f'{amount}.'
                            )
                        )

            client.save()

        log.info((
            f'[ {instance.get_type().label} ] Создана транзакция баллов '
            f'клиента. Кол-во баллов для зачисления/списания: '
            f'{instance.count}. Примечание: {instance.message} - '
            f'[ Дополнительные данные: {instance.__dict__} ]'
        ))
