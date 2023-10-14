from apps.base.models import Review
from rest_framework import serializers

from .client import ClientSafeSerializer


class ReviewSafeSerializer(serializers.ModelSerializer):
    client = ClientSafeSerializer()

    class Meta:
        model = Review
        fields = '__all__'
