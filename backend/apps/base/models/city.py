from django.db import models


class City(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ('-id',)

    def __str__(self):
        return self.name
