from config.celery import app
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from ..models import Push
from ..tasks import send_push_notifications


@receiver(post_save, sender=Push)
def push_post_save(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_status_waiting:
            if instance.audience is None:
                clients = instance.wallet.clients.not_deleted()
            else:
                clients = instance.audience.get_clients()

            args = [list(clients.values_list('id', flat=True)), instance.id]

            if instance.is_send_immediately:
                task = send_push_notifications.apply_async(
                    args=args, countdown=15)
            else:
                task = send_push_notifications.apply_async(
                    args=args, eta=instance.send_at)

            instance.task_id = task.task_id
            instance.save()


@receiver(pre_delete, sender=Push)
def push_pre_delete(sender, instance, **kwargs):
    if instance.task_id is not None:
        app.control.revoke(instance.task_id, terminate=True)
