from datetime import date

from config.celery import app
from django.db import models

from ..models import Bonus, Client, Wallet


@app.task
def start_the_burning_of_customer_points():
    """
    Запоминаем текущую дату.
    """
    today = date.today()

    """
    Ищем клиентов у которых тип карты: Бонусная карта, есть транзакции баллов
    с типом операции: Зачисление, есть не сгоревшие баллы, а так-же есть баллы
    у которых прошел срок действия.
    """
    clients = Client.objects.filter(
        wallet__type=Wallet.Type.BONUS,
        t_bonuses__type=Bonus.Type.CREDIT,
        t_bonuses__is_burned_bonuses=False,
        t_bonuses__expires_at__lte=today
    ).annotate(
        sum=models.Sum(
            't_bonuses__count'
        )
    ).distinct()

    if clients:
        ids = []
        t_bonuses = []

        """
        В цикле у каждого клиента вычитаем N баллов и добавляем в массив
        транзакцию баллов клиента.
        """
        for client in clients:
            ids.append(client.id)

            if client.sum > client.balance:
                subtract = client.balance
            else:
                subtract = client.sum

            client.balance -= subtract

            t_bonuses.append(
                Bonus(
                    is_auto_update_client=False,
                    client=client,
                    type=Bonus.Type.DEBIT,
                    count=subtract,
                    message='Сгорание неиспользованных баллов.'
                )
            )

        """
        У всех клиентов обновляем поле `balance`.
        """
        Client.objects.bulk_update(clients, ['balance'])

        """
        Массово создаем N записей в базе данных с транзакциями баллов.
        """
        Bonus.objects.bulk_create(t_bonuses)

        """
        Все не сгоревшие баллы отмечаем как сгоревшие.
        """
        Bonus.objects.filter(
            client__id__in=ids,
            type=Bonus.Type.CREDIT,
            is_burned_bonuses=False,
            expires_at__lte=today
        ).update(is_burned_bonuses=True)
