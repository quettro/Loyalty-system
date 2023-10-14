from django.db import models

from ...validators import check_if_the_wallet_has_been_deleted
from ..wallet import Wallet


class ServiceCategory(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта партнера',
        on_delete=models.PROTECT
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
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
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Категории услуг'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('wallet', 'name'),
                name='unique_service_category'
            ),
        )

    def __str__(self):
        return self.name

    def clean(self):
        if not self.id:
            if hasattr(self, 'wallet'):
                check_if_the_wallet_has_been_deleted(self.wallet)
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
