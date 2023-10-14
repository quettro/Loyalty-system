from django.core.validators import MinValueValidator
from django.db import models

from .category import ServiceCategory


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='services'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    amount = models.DecimalField(
        verbose_name='Стоимость',
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    is_use_cashback = models.BooleanField(
        verbose_name='Использовать скидки/кешбэк?',
        default=False
    )
    is_show = models.BooleanField(
        verbose_name='Отображать сервис?',
        default=False
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
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('category', 'name',),
                name='unique_service'
            ),
        )

    def __str__(self):
        return self.name
