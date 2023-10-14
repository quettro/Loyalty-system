from apps.base.regex import REGEX
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from ..managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    patronymic = models.CharField(
        verbose_name='Отчество',
        max_length=150,
        null=True,
        blank=True
    )
    phone = models.CharField(
        verbose_name='Номер телефона',
        max_length=12,
        validators=(RegexValidator(**REGEX['PHONE']),),
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)

        if self.patronymic:
            full_name = '%s %s' % (full_name, self.patronymic)

        return full_name.strip()

    @property
    def is_partner(self):
        return hasattr(self, 'partner') and self.partner is not None

    @property
    def is_employee(self):
        return hasattr(self, 'employee') and self.employee is not None

    def get_permissions(self):
        if self.is_partner:
            return self.partner.tariff.permissions

        elif self.is_employee:
            return self.employee.permissions

        return None

    def get_partner(self):
        if self.is_partner:
            return self.partner

        elif self.is_employee:
            return self.employee.partner

        return None
