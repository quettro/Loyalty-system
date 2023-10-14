from django.db import models


class PartnerType(models.Model):
    name = models.CharField(
        verbose_name='Наименование (ООО, ИП)',
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name = 'Тип партнера'
        verbose_name_plural = 'Типы партнеров'
        ordering = ('-id',)

    def __str__(self):
        return self.name
