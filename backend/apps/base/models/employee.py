from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from ..regex import REGEX
from .partner import Partner
from .permission import Permission


class Employee(models.Model):
    """ Данная модель отвечает за сотрудников партнера. """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='Доступы к разделам',
        related_name='employees',
        blank=True
    )
    note = models.TextField(
        verbose_name='Заметка',
        max_length=2048,
        null=True,
        blank=True
    )
    pincode = models.CharField(
        verbose_name='Пин-код',
        max_length=5,
        validators=(RegexValidator(**REGEX['PINCODE']),),
        help_text='Пин-код, необходимо вводить в формате: 0000.'
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
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ('-id',)

    def __str__(self):
        return self.user.get_full_name()

    def clean(self):
        if hasattr(self, 'user') and self.user is not None:
            if self.user.is_partner:
                raise ValidationError({
                    'user': [
                        (f'Партнера `{self.user.get_full_name()}` нельзя '
                         'назначить как сотрудника.')
                    ]
                })
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
