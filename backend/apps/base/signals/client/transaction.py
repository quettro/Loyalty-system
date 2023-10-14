import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ...models import Bonus, ClientTransaction

log = logging.getLogger(__name__)


@receiver(post_save, sender=ClientTransaction)
def transaction_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.amount > 0:
            """
            Создаем некий флаг `is_save_client`, чтобы при худшем раскладе не
            делать 2 запроса в базу данных для сохранения клиента.
            """
            is_save_client = False

            client = instance.client
            number_of_days_with_us = client.number_of_days_with_us
            wallet = client.wallet

            """
            Подсчитываем кол-во визитов клиента (visits), а так-же общую сумму
            покупок (amount).
            """
            transactions = client.transactions.aggregate(
                visits=models.Count('id', filter=models.Q(amount__gt=0)),
                amount=models.Sum('amount', filter=models.Q(amount__gt=0))
            )

            """
            Проверяем, получал ли клиент приветственные бонусы, если нет, то
            проверяем бонусная ли карта у клиента и выполнил ли он все условия
            для получения приветственных бонусов.
            """
            if not client.is_welcome_bonuses_received:
                _iuwb = wallet.is_use_welcome_bonuses
                _iitb = wallet.is_immediately_transfer_bonuses

                if wallet.is_type_bonus and _iuwb and not _iitb:
                    amount = transactions['amount']

                    if amount >= wallet.min_expenditure_obtaining_bonuses:
                        client.add_welcome_bonuses()
                        is_save_client = True

            """
            Ищем все статусы карты клиента у которых выполнены условия
            `Сумма покупок`, `Кол-во визитов` и
            `Кол-во дней с момента регистрации`.
            """
            statuses = wallet.statuses.filter(
                expenses__lte=transactions['amount'],
                visits__lte=transactions['visits'],
                number_of_days_with_us__lte=number_of_days_with_us)

            if client.status is not None:
                """
                Если у клиента есть статус, то исключаем текущий статус из
                выборки, а так-же ищем статусы у которых процент выше,
                чем на текущем.
                """
                statuses = statuses.exclude(id=client.status.id).filter(
                    percent__gt=client.status.percent)

            """
            Сортируем статусы по убыванию процентов и получаем первую запись.
            """
            status = statuses.order_by('-percent').first()

            if status is not None:
                """
                Если подходящий статус был найден, то присваиваем его клиенту.
                """
                client.status = status
                is_save_client = True

            """
            Проверяем, зачислить ли клиенту баллы автоматически.
            """
            if instance.is_auto_add_bonuses:
                bonuses = instance.amount / wallet.conversion
                bonuses = bonuses / 100 * instance.percent

                client.balance += bonuses
                is_save_client = True

                client.t_bonuses.create(
                    is_auto_update_client=False,
                    transaction=instance,
                    type=Bonus.Type.CREDIT,
                    count=bonuses,
                    message=(
                        f'Автоматическое зачисление баллов. '
                        f'Кэшбэк клиента: {instance.percent}%. '
                        f'Сумма покупок: {instance.amount}.'
                    )
                )

            """
            Если активен флаг `is_save_client`, сохраняем обновленные
            данные клиента.
            """
            if is_save_client:
                client.save()

        log.info((
            f'Создана транзакция клиента на сумму: {instance.amount}. '
            f'Примечание: {instance.message} - '
            f'[ Дополнительные данные: {instance.__dict__} ]'
        ))
