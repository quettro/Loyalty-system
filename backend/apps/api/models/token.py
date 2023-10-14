import binascii
import os

from django.conf import settings
from django.db import models


class CustomToken(models.Model):
    key = models.CharField(
        verbose_name='Ключ',
        max_length=40,
        primary_key=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='tokens',
        on_delete=models.CASCADE
    )
    ip = models.GenericIPAddressField(
        verbose_name='IP адрес',
        null=True,
        editable=False
    )
    browser_family = models.CharField(
        verbose_name='Браузер',
        null=True,
        max_length=255,
        editable=False
    )
    browser_version = models.CharField(
        verbose_name='Версия браузера',
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
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'
        ordering = ('-created_at',)

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        if self.browser_version is not None and len(self.browser_version) <= 0:
            self.browser_version = None

        if self.os_version is not None and len(self.os_version) <= 0:
            self.os_version = None

        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()
