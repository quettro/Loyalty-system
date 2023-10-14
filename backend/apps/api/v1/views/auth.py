from apps.api.models import CustomToken
from apps.base.utils import get_client_ip
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user_agents import parse


class ObtainAuthTokenViewSet(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_agent = request.META.get('HTTP_USER_AGENT')
        user_agent = parse(user_agent)

        token = CustomToken.objects.create(
            user=user,
            ip=get_client_ip(request),
            browser_family=user_agent.browser.family,
            browser_version=user_agent.browser.version_string,
            os_family=user_agent.os.family,
            os_version=user_agent.os.version_string,
            device_family=user_agent.device.family,
            device_brand=user_agent.device.brand,
            device_model=user_agent.device.model
        )

        return Response({'token': token.key})


class LogoutViewSet(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({'status': True})
