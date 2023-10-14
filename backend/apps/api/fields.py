from apps.base.models import Audience, ProductCategory, ServiceCategory
from rest_framework import serializers


def get_partner(request):
    return request.user.get_partner()


class CurrentPartnerHiddenField(
        serializers.HiddenField):
    """
    `CurrentPartnerHiddenField` переопределяет передаваемый параметр `default`
    на текущего партнера.
    """
    def __init__(self, **kwargs):
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_default(self):
        return get_partner(self.context.get('request'))


class CurrentPartnerCertsPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerCertsPrimaryKeyRelatedField` переопределяет `queryset`.
    Возвращает из базы данных все сертификаты текущего партнера.
    """
    def get_queryset(self):
        return get_partner(self.context.get('request')).certs.all()


class CurrentPartnerWalletsPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerWalletsPrimaryKeyRelatedField` переопределяет `queryset`.
    Возвращает из базы данных все не удаленные карты текущего партнера.
    """
    def get_queryset(self):
        return get_partner(self.context.get('request')).wallets.not_deleted()


class CurrentPartnerAudiencesPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerAudiencesPrimaryKeyRelatedField` переопределяет `queryset`.
    Возвращает из базы данных все аудитории текущего партнера.
    """
    def get_queryset(self):
        partner = get_partner(self.context.get('request'))
        return Audience.objects.filter(wallet__partner__id=partner.id)


class CurrentPartnerClientsPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerClientsPrimaryKeyRelatedField` переопределяет `queryset`.
    Возвращает из базы данных всех активных клиентов партнера.
    """
    def get_queryset(self):
        return get_partner(self.context.get('request')).clients.not_deleted()


class CurrentPartnerPermissionsPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerPermissionsPrimaryKeyRelatedField` переопределяет
    `queryset`. Возвращает из базы данных все доступы к разделам текущего
    партнера.
    """
    def get_queryset(self):
        return get_partner(
            self.context.get('request')
        ).tariff.permissions.filter(
            is_partners=False
        ).all()


class CurrentPartnerProductCategoriesPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerProductCategoriesPrimaryKeyRelatedField` переопределяет
    `queryset`. Возвращает из базы данных все категории товаров текущего
    партнера.
    """
    def get_queryset(self):
        return ProductCategory.objects.filter(
            wallet__partner__id=get_partner(self.context.get('request')).id,
            wallet__deleted_at=None
        ).all()


class CurrentPartnerServiceCategoriesPrimaryKeyRelatedField(
        serializers.PrimaryKeyRelatedField):
    """
    `CurrentPartnerServiceCategoriesPrimaryKeyRelatedField` переопределяет
    `queryset`. Возвращает из базы данных все категории услуг текущего
    партнера.
    """
    def get_queryset(self):
        return ServiceCategory.objects.filter(
            wallet__partner__id=get_partner(self.context.get('request')).id,
            wallet__deleted_at=None
        ).all()
