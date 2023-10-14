import random
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from libraries.pkpass import PkPass

from ...choices import ChoiceDict
from ...managers import ClientManager
from ...regex import REGEX
from ...validators import check_if_the_wallet_has_been_deleted
from ..partner import Partner
from ..status import Status
from ..wallet import Wallet
from .bonus import Bonus

from django.core.validators import (  # isort: skip
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)


class Client(models.Model):
    class Sex(ChoiceDict, models.TextChoices):
        MAN = 'MAN', 'Мужской'
        WOMAN = 'WOMAN', 'Женский'

    partner = models.ForeignKey(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='clients'
    )
    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта',
        on_delete=models.PROTECT,
        related_name='clients'
    )
    status = models.ForeignKey(
        Status,
        verbose_name='Статус карты',
        on_delete=models.SET_NULL,
        related_name='clients',
        null=True,
        blank=True
    )
    authentication_token = models.UUIDField(
        verbose_name='Токен авторизации',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    numbers = models.CharField(
        verbose_name='Номер карты',
        null=True,
        max_length=255,
        editable=False,
        unique=True
    )
    name = models.CharField(
        verbose_name='Наименование карты',
        max_length=255
    )
    sex = models.CharField(
        verbose_name='Пол',
        max_length=10,
        choices=Sex.choices
    )
    birthday = models.DateField(
        verbose_name='Дата рождения'
    )
    phone = models.CharField(
        verbose_name='Номер телефона',
        max_length=12,
        validators=(RegexValidator(**REGEX['PHONE']),)
    )

    """
    Бонусная карта
    """
    balance = models.DecimalField(
        verbose_name='Баланс',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )

    """
    Чоп карта
    """
    c_stamps = models.PositiveIntegerField(
        verbose_name='Сколько всего штампов было получено',
        default=0,
        validators=(MinValueValidator(0),)
    )
    a_stamps = models.PositiveSmallIntegerField(
        verbose_name='Активных штампов',
        default=0,
        validators=(
            MinValueValidator(0),
            MaxValueValidator(settings.MAX_STAMPS),
        )
    )
    a_rewards = models.PositiveSmallIntegerField(
        verbose_name='Активных наград',
        default=0,
        validators=(
            MinValueValidator(0),
            MaxValueValidator(settings.MAX_REWARDS),
        )
    )

    pkpass = models.FileField(
        verbose_name='PkPass',
        upload_to=f'{settings.PKPASS_DIRNAME}/',
        editable=False,
        null=True,
        blank=True,
        validators=(FileExtensionValidator(['pkpass']),)
    )
    is_welcome_bonuses_received = models.BooleanField(
        verbose_name='Получил ли приветственные бонусы?',
        default=False
    )
    deleted_at = models.DateTimeField(
        verbose_name='Дата удаления карты (Мягкое удаление)',
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления',
        auto_now=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    objects = ClientManager()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('wallet', 'phone'),
                name='unique_client_for_wallet'
            ),
        )

    def __str__(self):
        return f'Name: {self.name} | Deleted at: {self.deleted_at}'

    def clean(self):
        if hasattr(self, 'wallet') and self.wallet is not None:
            if not self.id:
                check_if_the_wallet_has_been_deleted(self.wallet)

                if hasattr(self, 'partner') and self.partner is not None:
                    if self.partner.is_max_clients:
                        if not self.partner.is_it_possible_deduct_from_balance(
                            self.partner.tariff.cost_additional_client
                        ):
                            raise ValidationError({
                                'partner': [
                                    'Достигнут лимит по созданию клиентов.'
                                ]
                            })

            if hasattr(self, 'status') and self.status is not None:
                if self.wallet.id != self.status.wallet.id:
                    raise ValidationError({
                        'status': [
                            'Данный статус не относится к выбранной карте.'
                        ]
                    })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.id:
            self.override_numbers()
            self.override_pkpass()

        return super().save(*args, **kwargs)

    @property
    def number_of_days_with_us(self):
        """
        Получить кол-во дней прошедших с момента регистрации.
        """
        return (timezone.now() - self.created_at).days

    @property
    def cashback(self):
        """
        Получить актуальный кэшбэк клиента.
        """
        percent = self.status.percent if self.status else self.wallet.cashback
        percent += self.get_max_increased_percentage()

        return 100 if percent > 100 else percent

    @property
    def discount(self):
        """
        Получить актуальную скидку клиента.
        """
        percent = self.status.percent if self.status else self.wallet.discount
        percent += self.get_max_increased_percentage()

        return 100 if percent > 100 else percent

    @property
    def is_deleted(self):
        """
        Проверка, удален ли клиент
        """
        return self.deleted_at is not None

    def get_max_increased_percentage(self):
        """
        Получить актуальный, максимально повышенный процент клиента.
        """
        percent = self.percentages.filter(
            activated_at__lte=timezone.now(), expires_at__gte=timezone.now()
        ).aggregate(max=models.Max('percent'))['max']

        return 0 if percent is None else percent

    def get_sex(self):
        return self.Sex(self.sex)

    def get_sex_dict(self):
        return self.get_sex().dict()

    def get_phone(self):
        if self.partner.is_show_client_phones:
            return self.phone
        return f'{self.phone[:-4]}****'

    def add_welcome_bonuses(self):
        """
        Зачислить приветственные бонусы клиенту без сохранения в базу данных.
        """
        self.is_welcome_bonuses_received = True

        self.t_bonuses.create(
            type=Bonus.Type.CREDIT,
            count=self.wallet.bonuses,
            message='Зачисление приветственного бонуса.'
        )

    def softdelete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def override_numbers(self):
        snumbers = self.wallet.snumbers

        self.numbers = random.randint(10000000000, 20000000000)
        self.numbers = f'{snumbers}{self.numbers}'

        while Client.objects.filter(numbers=self.numbers).exists():
            self.numbers = random.randint(10000000000, 20000000000)
            self.numbers = f'{snumbers}{self.numbers}'

    def override_pkpass(self, message=None):
        pkpass = PkPass(self, message).create()
        pkpass = str(pkpass).replace(str(settings.MEDIA_ROOT), '')[1:]
        self.pkpass.name = pkpass
