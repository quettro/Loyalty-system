from apps.base.models import Employee
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .permission import PermissionSerializer
from .user import CustomUserSerializer

from ...fields import (  # isort: skip
    CurrentPartnerHiddenField,
    CurrentPartnerPermissionsPrimaryKeyRelatedField
)


class EmployeeSafeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Employee
        exclude = ('partner',)


class EmployeeNotSafeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    partner = CurrentPartnerHiddenField()
    permissions = CurrentPartnerPermissionsPrimaryKeyRelatedField(many=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def save(self, **kwargs):
        user = self.validated_data.pop('user', None)

        if user is not None:
            params = {'data': user, 'partial': self.partial}

            if self.instance:
                params['instance'] = self.instance.user

            user_serializer = CustomUserSerializer(**params)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

            self.validated_data['user'] = user

        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
