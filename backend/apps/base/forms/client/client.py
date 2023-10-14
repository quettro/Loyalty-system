from django import forms

from ...models import Client


class ClientAdminForm(forms.ModelForm):
    is_update_pkpass = forms.BooleanField(
        label='Обновить .pkpass клиента?', required=False)

    class Meta:
        model = Client
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            self.fields['is_update_pkpass'].disabled = True

    def save(self, *args, **kwargs):
        if self.instance.id is not None:
            if self.cleaned_data['is_update_pkpass']:
                self.instance.override_pkpass()
        return super().save(*args, **kwargs)
