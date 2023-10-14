from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from ...models import Client, IncreasedPercentage, PartnerTransaction


@receiver(post_save, sender=Client)
def client_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.partner.is_max_clients:
            instance.partner.transactions.create(
                type=PartnerTransaction.Type.DEBIT,
                amount=instance.partner.tariff.cost_additional_client,
                message=(
                    f'Списание средств за дополнительного клиента. '
                    f'Клиент: [ {instance.numbers} | {instance.name} ]. '
                    f'Карта: [ {instance.wallet.uuid} | '
                    f'{instance.wallet.name} ].'
                )
            )

        triggers = instance.wallet.triggers.filter(
            is_increased_percentage=True)

        if triggers:
            percentages = []

            for trigger in triggers:
                if trigger.audience is not None:
                    if trigger.audience.get_clients().filter(
                        id=instance.id
                    ).count() <= 0:
                        continue

                expires_at = trigger.launch_at + timedelta(
                    days=trigger.days_after_the_event)

                if expires_at >= timezone.now():
                    activated_at = trigger.launch_at - timedelta(
                        days=trigger.days_before_the_event)

                    percentages.append(
                        IncreasedPercentage(
                            client=instance,
                            trigger=trigger,
                            percent=trigger.percent,
                            activated_at=activated_at,
                            expires_at=expires_at
                        )
                    )

            if percentages:
                IncreasedPercentage.objects.bulk_create(percentages)

        if not instance.is_welcome_bonuses_received:
            if instance.wallet.is_type_bonus:
                if instance.wallet.is_use_welcome_bonuses:
                    if instance.wallet.is_immediately_transfer_bonuses:
                        instance.add_welcome_bonuses()
                        instance.save()
