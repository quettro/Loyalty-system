from dateutil import parser
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from OpenSSL import crypto

from .partner import Partner


class Cert(models.Model):
    """ Данная модель отвечает за сертификаты IOS. """

    partner = models.ForeignKey(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='certs'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    p12_cert = models.FileField(
        verbose_name='(.p12) Сертификат',
        upload_to='certs/.p12/%Y/%m/%d/',
        validators=(FileExtensionValidator(['p12']),)
    )
    p12_password = models.CharField(
        verbose_name='(.p12) Пароль',
        max_length=255
    )
    p12_cert_pem = models.FileField(
        verbose_name='(.p12) Сертификат.pem',
        upload_to='certs/.p12/%Y/%m/%d/',
        validators=(FileExtensionValidator(['pem']),),
        null=True,
        blank=True
    )
    p12_cert_key = models.FileField(
        verbose_name='(.p12) Сертификат.key',
        upload_to='certs/.p12/%Y/%m/%d/',
        validators=(FileExtensionValidator(['key']),),
        null=True,
        blank=True
    )
    p12_organization_name = models.CharField(
        verbose_name='(.p12) Организация',
        max_length=255,
        null=True,
        blank=True
    )
    p12_team_identifier = models.CharField(
        verbose_name='(.p12) Подразделение',
        max_length=255,
        null=True,
        blank=True
    )
    p12_pass_type_identifier = models.CharField(
        verbose_name='(.p12) Идентификатор пользователя',
        max_length=255,
        null=True,
        blank=True
    )
    p12_activated_at = models.DateTimeField(
        verbose_name=(
            'Отметка времени, с которой сертификат начинает '
            'действовать'
        ),
        null=True,
        blank=True
    )
    p12_expires_at = models.DateTimeField(
        verbose_name=(
            'Отметка времени, при которой сертификат перестает '
            'быть действительным'
        ),
        null=True,
        blank=True
    )
    p8_cert = models.FileField(
        verbose_name='(.p8) Сертификат',
        upload_to='certs/.p8/%Y/%m/%d/',
        validators=(FileExtensionValidator(['p8']),)
    )
    p8_key = models.CharField(
        verbose_name='(.p8) Идентификатор ключа (Key ID)',
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
        verbose_name = 'Сертификат IOS'
        verbose_name_plural = 'Сертификаты IOS'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('partner', 'name'),
                name='unique_cert_by_partner'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__p12_cert = self.p12_cert

    def __str__(self):
        return self.name

    def clean(self):
        if not self.id or self.p12_cert != self.__p12_cert:
            try:
                p12 = crypto.load_pkcs12(
                    self.p12_cert.open().read(),
                    self.p12_password.encode()
                )
            except Exception:
                raise ValidationError({
                    'p12_cert': [
                        ('Не удалось открыть сертификат. Возможно, указан '
                         'некорректный пароль.')
                    ]
                })

            p12_cert = p12.get_certificate()

            if p12_cert.has_expired():
                pass
                """
                raise ValidationError({
                    'p12_cert': [
                        ('Срок действия сертификата истек. '
                         'Загрузите новый сертификат.')
                    ]
                })
                """

            p12_cert_pem = crypto.dump_certificate(
                crypto.FILETYPE_PEM, p12_cert)
            p12_cert_key = crypto.dump_privatekey(
                crypto.FILETYPE_PEM, p12.get_privatekey())

            self.p12_cert_pem.save(
                'p12.pem', ContentFile(p12_cert_pem), save=False)
            self.p12_cert_key.save(
                'p12.key', ContentFile(p12_cert_key), save=False)

            p12_activated_at = p12_cert.get_notBefore().decode('UTF-8')
            self.p12_activated_at = parser.parse(p12_activated_at)

            p12_expires_at = p12_cert.get_notAfter().decode('UTF-8')
            self.p12_expires_at = parser.parse(p12_expires_at)

            self.p12_organization_name = p12_cert.get_subject().O
            self.p12_team_identifier = p12_cert.get_subject().OU
            self.p12_pass_type_identifier = p12_cert.get_subject().UID

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def p12_days_left(self):
        """
        Получить оставшийся срок действия сертификата в днях.
        """
        days = (self.p12_expires_at - timezone.now()).days
        return days if days > 0 else 0
