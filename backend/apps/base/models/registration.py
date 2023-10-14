from django.db import models

from .client import Client


class Registration(models.Model):
    """
    Модель отвечает за регистрацию пропуска на устройстве.
    """
    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        on_delete=models.PROTECT,
        related_name='registrations'
    )
    device_library_id = models.CharField(
        verbose_name='Уникальный идентификатор устройства',
        null=True,
        max_length=255,
        editable=False
    )
    push_token = models.CharField(
        verbose_name='Пуш токен',
        null=True,
        max_length=255,
        editable=False
    )
    os_family = models.CharField(
        verbose_name='Операционная система',
        null=True,
        max_length=255,
        editable=False
    )
    os_version = models.CharField(
        verbose_name='Версия операционной системы',
        null=True,
        max_length=255,
        editable=False
    )
    device_family = models.CharField(
        verbose_name='Устройство',
        null=True,
        max_length=255,
        editable=False
    )
    device_brand = models.CharField(
        verbose_name='Бренд устройства',
        null=True,
        max_length=255,
        editable=False
    )
    device_model = models.CharField(
        verbose_name='Модель устройства',
        null=True,
        max_length=255,
        editable=False
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления',
        auto_now=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
        ordering = ('-id',)

    def __str__(self):
        return self.device_library_id

    def clean(self):
        if self.os_version is not None and len(self.os_version) <= 0:
            self.os_version = None
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
