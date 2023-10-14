from rest_framework.permissions import SAFE_METHODS


class SerializersMixin:
    safe_serializer = None
    not_safe_serializer = None

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return self.safe_serializer
        return self.not_safe_serializer
