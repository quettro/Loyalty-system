from django.core.validators import RegexValidator
from django.db import models

from ..regex import REGEX
from .city import City


class Company(models.Model):
    city = models.ForeignKey(
        City,
        verbose_name='Город',
        on_delete=models.PROTECT,
        related_name='companies'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=13,
        validators=(RegexValidator(**REGEX['INN']),)
    )
    bik = models.CharField(
        verbose_name='Бик',
        max_length=10,
        validators=(RegexValidator(**REGEX['BIK']),)
    )
    rs = models.CharField(
        verbose_name='Расчётный счёт (Р/с)',
        max_length=21,
        validators=(RegexValidator(**REGEX['RS']),)
    )
    ks = models.CharField(
        verbose_name='Корреспонденский счёт (К/с)',
        max_length=21,
        validators=(RegexValidator(**REGEX['KS']),)
    )
    yur_address = models.CharField(
        verbose_name='Юридический адрес',
        max_length=255
    )
    fact_address = models.CharField(
        verbose_name='Фактический адрес',
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
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ('-id',)

    def __str__(self):
        return self.name
