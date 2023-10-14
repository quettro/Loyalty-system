from apps.users.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'patronymic',
            'phone',
        )

        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'password': {
                'write_only': True
            }
        }

    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return password

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        instance.set_password(self.validated_data.get('password'))
        instance.save()
        return instance
