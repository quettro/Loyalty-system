from django.db import models


class WalletQuerySet(models.query.QuerySet):
    def not_deleted(self):
        return self.filter(deleted_at=None)


class ClientQuerySet(models.query.QuerySet):
    def not_deleted(self):
        return self.filter(deleted_at=None)

    def wallet_not_deleted(self):
        return self.filter(wallet__deleted_at=None)


class TriggerQuerySet(models.query.QuerySet):
    def wallet_not_deleted(self):
        return self.filter(wallet__deleted_at=None)
