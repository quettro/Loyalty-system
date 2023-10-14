from apps.base.models import Partner
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.db import models


class Contract(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255,
        unique=True
    )
    version = models.CharField(
        verbose_name='Версия договора',
        max_length=32
    )
    content = RichTextUploadingField(
        verbose_name='Содержимое'
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
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.id:
            if Contract.objects.count() > 0:
                raise ValidationError(
                    'Невозможно создать более 1-го договора.')
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class AcceptedContract(models.Model):
    partner = models.OneToOneField(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='contract'
    )
    contract = models.ForeignKey(
        Contract,
        verbose_name='Договор',
        on_delete=models.PROTECT,
        related_name='partners'
    )
    ip = models.GenericIPAddressField(
        verbose_name='IP адрес',
        null=True,
        editable=False
    )
    browser_family = models.CharField(
        verbose_name='Браузер',
        null=True,
        max_length=255,
        editable=False
    )
    browser_version = models.CharField(
        verbose_name='Версия браузера',
        null=True,
        max_length=255,
        editable=False
    )
    os_family = models.CharField(
        verbose_name='Операционная система',
        null=True,
        max_length=255,
        editable=False
    )
    os_version = models.CharField(
        verbose_name='Версия операционной системы',
        null=True,
        max_length=255,
        editable=False
    )
    device_family = models.CharField(
        verbose_name='Устройство',
        null=True,
        max_length=255,
        editable=False
    )
    device_brand = models.CharField(
        verbose_name='Бренд устройства',
        null=True,
        max_length=255,
        editable=False
    )
    device_model = models.CharField(
        verbose_name='Модель устройства',
        null=True,
        max_length=255,
        editable=False
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
        verbose_name = 'Принятый договор'
        verbose_name_plural = 'Принятые договоры'
        ordering = ('-id',)

    def __str__(self):
        return self.contract.name

    def clean(self):
        if self.browser_version is not None and len(self.browser_version) <= 0:
            self.browser_version = None

        if self.os_version is not None and len(self.os_version) <= 0:
            self.os_version = None

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
