from django import forms

from ..models import Partner


class PartnerAdminForm(forms.ModelForm):
    is_individual_tariff = forms.BooleanField(
        label='Привязать выбранный тариф к партнеру как индивидуальный?',
        required=False)

    class Meta:
        model = Partner
        fields = '__all__'

        widgets = {
            'address': forms.Textarea(
                attrs={
                    'cols': 100,
                    'rows': 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        """
        Проверяем, создан ли партнер, если создан, то
        проверяем, индивидуальный ли тариф у партнера, если да,
        активируем checkbox `is_individual_tariff`.
        """
        if self.instance:
            try:
                if self.instance.tariff.is_individual:
                    checkbox = self.fields['is_individual_tariff']
                    checkbox.widget.attrs['checked'] = 'checked'
            except Exception:
                pass

    def clean(self):
        tariff = self.cleaned_data.get('tariff')
        checkbox = self.cleaned_data.get('is_individual_tariff')

        if not tariff:
            return super().clean()

        """
        Выбрасываем ошибку, если выбран индивидуальный тариф, так же
        если партнер еще не создан или создан, но тариф не привязан к данному
        партнеру.
        """
        if(
            tariff.is_individual and (
                not self.instance or (
                    self.instance and self.instance.id != tariff.partner.id
                )
            )
        ):
            message = (
                f'Тариф: {tariff.name}, не может быть выбран, т.к '
                f'принадлежит партнеру: {tariff.partner}'
            )
            self._errors['tariff'] = self.error_class([message])

        """
        Выбрасываем ошибку, если хотят сделать занятый кем-то тариф
        индивидуальным.
        """
        if checkbox:
            objects = Partner.objects.filter(tariff__id=tariff.id)

            if self.instance:
                objects = objects.exclude(id=self.instance.id)

            if objects.exists():
                message = (
                    f'Тариф: {tariff.name}, не может быть выбран как '
                    'индивидуальный, т.к он используется кем-то.'
                )
                self._errors['tariff'] = self.error_class([message])

        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        """
        Проверяем, если checkbox `is_individual_tariff` активирован,
        то проверяем, индивидуальный ли тариф, если нет, привязываем тариф к
        партнеру. Если checkbox не активирован, проверяем, индивидуальный ли
        тариф, если да, то обнуляем поле `partner` у тарифа.
        """
        if self.cleaned_data.get('is_individual_tariff', False):
            if not self.instance.tariff.is_individual:
                self.instance.update_tariff_partner(self.instance)
        else:
            if self.instance.tariff.is_individual:
                self.instance.update_tariff_partner()

        return self.instance
