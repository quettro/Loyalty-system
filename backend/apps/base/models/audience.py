from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from ..choices import ChoiceDict
from ..validators import check_if_the_wallet_has_been_deleted
from .wallet import Wallet


class Audience(models.Model):
    class Sex(ChoiceDict, models.TextChoices):
        MAN = 'MAN', 'Мужской'
        WOMAN = 'WOMAN', 'Женский'
        ALL = 'ALL', 'Все'

    class Device(ChoiceDict, models.TextChoices):
        ANDROID = 'ANDROID', 'Android'
        IOS = 'IOS', 'iOS'
        ALL = 'ALL', 'Все устройства'

    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта',
        on_delete=models.PROTECT,
        related_name='audiences'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    is_use_age = models.BooleanField(
        verbose_name='Исп. фильтрацию по возрасту?',
        default=False
    )
    min_age = models.PositiveSmallIntegerField(
        verbose_name='Минимальный возраст',
        default=0,
        validators=(MinValueValidator(0),)
    )
    max_age = models.PositiveSmallIntegerField(
        verbose_name='Максимальный возраст',
        default=100,
        validators=(MaxValueValidator(100),)
    )
    is_use_birthday = models.BooleanField(
        verbose_name='Исп. фильтрацию по дню рождения?',
        default=False
    )
    min_birthday = models.PositiveSmallIntegerField(
        verbose_name='Минимальное число дня рождения',
        default=1,
        validators=(MinValueValidator(1),)
    )
    max_birthday = models.PositiveSmallIntegerField(
        verbose_name='Максимальное число дня рождения',
        default=31,
        validators=(MaxValueValidator(31),)
    )
    is_use_days_from_registration = models.BooleanField(
        verbose_name='Исп. фильтрацию по кол-ву дней с момента регистрации?',
        default=False
    )
    min_days_from_registration = models.PositiveSmallIntegerField(
        verbose_name='Минимальное кол-во дней с момента регистрации',
        default=0,
        validators=(MinValueValidator(0),)
    )
    max_days_from_registration = models.PositiveSmallIntegerField(
        verbose_name='Максимальное кол-во дней с момента регистрации',
        default=3650,
        validators=(MaxValueValidator(3650),)
    )
    is_use_average_check = models.BooleanField(
        verbose_name='Исп. фильтрацию по среднему чеку?',
        default=False
    )
    min_average_check = models.PositiveSmallIntegerField(
        verbose_name='Минимальный средний чек',
        default=0,
        validators=(MinValueValidator(0),)
    )
    max_average_check = models.PositiveSmallIntegerField(
        verbose_name='Максимальный средний чек',
        default=30000,
        validators=(MaxValueValidator(30000),)
    )
    is_use_visits = models.BooleanField(
        verbose_name='Исп. фильтрацию по кол-во визитам?',
        default=False
    )
    min_visits = models.PositiveSmallIntegerField(
        verbose_name='Минимальное кол-во визитов',
        default=0,
        validators=(MinValueValidator(0),)
    )
    max_visits = models.PositiveSmallIntegerField(
        verbose_name='Максимальное кол-во визитов',
        default=10000,
        validators=(MaxValueValidator(10000),)
    )
    sex = models.CharField(
        verbose_name='Пол',
        max_length=10,
        choices=Sex.choices
    )
    device = models.CharField(
        verbose_name='Устройство',
        max_length=20,
        choices=Device.choices
    )
    is_visited_the_institution = models.BooleanField(
        verbose_name='Посещал заведение?',
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
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.id:
            if hasattr(self, 'wallet'):
                check_if_the_wallet_has_been_deleted(self.wallet)

        validators = {
            'is_use_age': {
                'min': 'min_age',
                'max': 'max_age'
            },
            'is_use_birthday': {
                'min': 'min_birthday',
                'max': 'max_birthday'
            },
            'is_use_days_from_registration': {
                'min': 'min_days_from_registration',
                'max': 'max_days_from_registration'
            },
            'is_use_average_check': {
                'min': 'min_average_check',
                'max': 'max_average_check'
            },
            'is_use_visits': {
                'min': 'min_visits',
                'max': 'max_visits'
            }
        }

        for key, item in validators.items():
            if getattr(self, key) is True:
                if getattr(self, item['min']) > getattr(self, item['max']):
                    raise ValidationError({
                        item['min']: [
                            ('Минимальное значение не может превышать '
                                'максимальное.')
                        ]
                    })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_sex_all(self):
        return self.sex == self.Sex.ALL

    @property
    def is_device_all(self):
        return self.device == self.Device.ALL

    def get_sex(self):
        return self.Sex(self.sex)

    def get_sex_dict(self):
        return self.get_sex().dict()

    def get_device(self):
        return self.Device(self.device)

    def get_device_dict(self):
        return self.get_device().dict()

    def get_clients(self):
        objects = self.wallet.clients.not_deleted().filter(
            **self.get_filters_without_annotate())

        if self.is_use_average_check:
            objects = objects.annotate(
                transactions_amount=models.Avg(
                    'transactions__amount',
                    filter=models.Q(transactions__amount__gt=0)
                )
            ).filter(
                transactions_amount__gte=self.min_average_check,
                transactions_amount__lte=self.max_average_check
            )

        if self.is_use_visits or self.is_visited_the_institution:
            objects = objects.annotate(
                visits=models.Count(
                    'transactions',
                    filter=models.Q(transactions__amount__gt=0)
                )
            )

            if self.is_use_visits:
                objects = objects.filter(
                    visits__gte=self.min_visits,
                    visits__lte=self.max_visits
                )

            if self.is_visited_the_institution:
                objects = objects.filter(visits__gt=0)

        return objects # noqa

    def get_filters_without_annotate(self):
        filters = {}

        if not self.is_sex_all:
            filters['sex'] = self.sex

        if self.is_use_birthday:
            filters['birthday__day__gte'] = self.min_birthday
            filters['birthday__day__lte'] = self.max_birthday

        if not self.is_device_all:
            filters['registrations__os_family__iexact'] = self.get_device(
            ).label

        if self.is_use_days_from_registration:
            filters['created_at__lte'] = (timezone.now() - timedelta(
                days=self.min_days_from_registration))

            filters['created_at__gte'] = (timezone.now() - timedelta(
                days=self.max_days_from_registration))

        if self.is_use_age:
            filters['birthday__range'] = [
                (timezone.now() - timedelta(
                    days=((self.max_age + 1) * 365))).replace(
                        hour=0, minute=0, second=0, microsecond=0),
                (timezone.now() - timedelta(
                    days=(self.min_age * 365))).replace(
                        hour=0, minute=0, second=0, microsecond=0),
            ]

        return filters
