from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import IncreasedPercentage, Trigger


@receiver(post_save, sender=Trigger)
def trigger_post_save(sender, instance, created, *args, **kwargs):
    if not created:
        IncreasedPercentage.objects.filter(trigger__id=instance.id).delete()

    if instance.is_increased_percentage:
        if instance.audience is None:
            clients = instance.wallet.clients.not_deleted().values_list(
                'id', flat=True)
        else:
            clients = instance.audience.get_clients().values_list(
                'id', flat=True)

        activated_at = instance.launch_at - timedelta(
            days=instance.days_before_the_event)

        expires_at = instance.launch_at + timedelta(
            days=instance.days_after_the_event)

        IncreasedPercentage.objects.bulk_create([
            IncreasedPercentage(
                client_id=client,
                trigger=instance,
                percent=instance.percent,
                activated_at=activated_at,
                expires_at=expires_at
            ) for client in clients
        ])
