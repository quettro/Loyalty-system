from django.db import models

from .querysets import ClientQuerySet, TriggerQuerySet, WalletQuerySet


class WalletManager(models.Manager):
    def get_queryset(self):
        return WalletQuerySet(self.model, using=self._db)

    def not_deleted(self):
        return self.get_queryset().not_deleted()


class ClientManager(models.Manager):
    def get_queryset(self):
        return ClientQuerySet(self.model, using=self._db)

    def not_deleted(self):
        return self.get_queryset().not_deleted()

    def wallet_not_deleted(self):
        return self.get_queryset().wallet_not_deleted()


class TriggerManager(models.Manager):
    def get_queryset(self):
        return TriggerQuerySet(self.model, using=self._db)

    def wallet_not_deleted(self):
        return self.get_queryset().wallet_not_deleted()
