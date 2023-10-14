from django import forms
from django.core.exceptions import ValidationError

from ...models import Bonus, ClientTransaction, Wallet


class ClientTransactionAdminForm(forms.ModelForm):
    is_auto_add_bonuses = forms.BooleanField(
        label='Начислить баллы автоматически?', required=False)

    class Meta:
        model = ClientTransaction
        fields = '__all__'

    def clean(self):
        client = self.cleaned_data.get(
            'client')
        is_auto_add_bonuses = self.cleaned_data.get(
            'is_auto_add_bonuses', False)

        if client is not None and is_auto_add_bonuses:
            if not client.wallet.is_type_bonus:
                raise ValidationError({
                    'is_auto_add_bonuses': [
                        ('Тип карты клиента не соответствует типу: '
                            f'{Wallet.Type.BONUS.label}')
                    ]
                })

        return super().clean()

    def save(self, *args, **kwargs):
        is_auto_add_bonuses = self.cleaned_data.pop('is_auto_add_bonuses')
        instance = super().save(*args, **kwargs)

        if is_auto_add_bonuses:
            bonuses = instance.amount / instance.client.wallet.conversion
            bonuses = bonuses / 100 * instance.percent

            instance.client.t_bonuses.create(
                type=Bonus.Type.CREDIT,
                count=bonuses,
                message=(
                    f'Автоматическое зачисление баллов. '
                    f'Кэшбэк клиента: {instance.percent}%. '
                    f'Сумма покупок: {instance.amount}.'
                )
            )

        return instance
