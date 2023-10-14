from apps.base.models import Client
from config.celery import app
from django.db import models


@app.task
def statuses():
    updated = []

    """
    Ищем активных клиентов подсчитывая кол-во визитов и общую сумму
    покупок. Отсеиваем клиентов, если у карты клиента нет статусов.
    """
    clients = Client.objects.not_deleted().wallet_not_deleted().annotate(
        visits=models.Count(
            'transactions', filter=models.Q(
                transactions__amount__gt=0
            )
        ),
        transactions_amount=models.Sum(
            'transactions__amount', filter=models.Q(
                transactions__amount__gt=0
            )
        ),
        statuses=models.Count('wallet__statuses')
    ).filter(statuses__gt=0)

    for client in clients:
        number_of_days_with_us = client.number_of_days_with_us

        """
        Ищем все статусы карты клиента у которых выполнены условия
        `Сумма покупок`, `Кол-во визитов` и
        `Кол-во дней с момента регистрации`.
        """
        statuses = client.wallet.statuses.filter(
            expenses__lte=client.transactions_amount,
            visits__lte=client.visits,
            number_of_days_with_us__lte=number_of_days_with_us)

        if client.status is not None:
            """
            Если у клиента есть статус, то исключаем текущий статус из выборки,
            а так-же ищем статусы у которых процент выше, чем на текущем.
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
            updated.append(client)

    Client.objects.bulk_update(updated, ['status', 'pkpass'])
