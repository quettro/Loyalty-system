from django import forms

from ..models import AcceptedContract, Contract


class ContractAdminForm(forms.ModelForm):
    is_reset_accepted_contracts = forms.BooleanField(
        label='Сбросить принятые договоры у партнеров?', required=False)

    class Meta:
        model = Contract
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            self.fields['is_reset_accepted_contracts'].disabled = True

    def save(self, *args, **kwargs):
        if self.instance.id is not None:
            if self.cleaned_data['is_reset_accepted_contracts']:
                AcceptedContract.objects.filter(
                    contract__id=self.instance.id
                ).delete()
        return super().save(*args, **kwargs)
