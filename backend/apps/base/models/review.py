from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .client import Client


class Review(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        on_delete=models.PROTECT,
        related_name='reviews'
    )
    ip = models.GenericIPAddressField(
        verbose_name='Ip адрес'
    )
    message = models.TextField(
        verbose_name='Сообщение',
        max_length=2048
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=(MinValueValidator(1), MaxValueValidator(3),)
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
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-id',)

    def __str__(self):
        return self.message
