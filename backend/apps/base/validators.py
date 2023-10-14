from django.core.exceptions import ValidationError


def check_if_the_wallet_has_been_deleted(wallet):
    if wallet is not None and wallet.is_deleted:
        raise ValidationError({
            'wallet': [
                'Невозможно выбрать данную карту, т.к карта приостановлена.'
            ]
        })
