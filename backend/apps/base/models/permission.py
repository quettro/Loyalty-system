from django.db import models


class Permission(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255,
        unique=True,
        help_text='Например: Добавление товаров'
    )
    codename = models.CharField(
        verbose_name='Кодовое наименование',
        max_length=255,
        unique=True,
        help_text='Например: add_products'
    )
    is_partners = models.BooleanField(
        verbose_name='Доступ к данному разделу имеют только партнеры?',
        default=False
    )

    class Meta:
        verbose_name = 'Доступ'
        verbose_name_plural = 'Доступы'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name} | {self.codename} | {self.is_partners}'
