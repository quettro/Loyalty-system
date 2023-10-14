from django.core.validators import MinValueValidator
from django.db import models

from .category import ProductCategory


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='Категория',
        on_delete=models.PROTECT,
        related_name='products'
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
        verbose_name='Отображать товар?',
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
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('category', 'name',),
                name='unique_product'
            ),
        )

    def __str__(self):
        return self.name
