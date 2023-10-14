from django import forms
from prettyjson import PrettyJSONWidget

from ..models import Wallet


class WalletAdminForm(forms.ModelForm):
    is_delete = forms.BooleanField(
        label='Произвести мягкое удаление?', required=False)

    class Meta:
        model = Wallet
        fields = '__all__'

        widgets = {
            'geolocations': PrettyJSONWidget(),
            'frontend': PrettyJSONWidget(),
            'backend': PrettyJSONWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            self.fields['is_delete'].disabled = True
        else:
            if self.instance.is_deleted:
                checkbox = self.fields['is_delete']
                checkbox.widget.attrs['checked'] = 'checked'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.instance.id is not None:
            is_delete = self.cleaned_data.get('is_delete', False)

            if self.instance.is_deleted:
                if not is_delete:
                    self.instance.restore()
            else:
                if is_delete:
                    self.instance.softdelete()

        return self.instance
