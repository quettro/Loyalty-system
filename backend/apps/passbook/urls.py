from django.urls import path

from . import views

app_name = 'passbook'

urlpatterns = [
    path(
        (
            r'v1/devices/<str:device_library_id>/'
            r'registrations/<str:pass_type_id>/<str:serial_number>'
        ),
        views.RegisterPassViewSet.as_view(),
        name='register_pass'
    ),
    path(
        (
            r'v1/devices/<str:device_library_id>/'
            r'registrations_attido/<str:pass_type_id>/<str:serial_number>'
        ),
        views.RegisterPassViewSet.as_view(),
        name='register_pass'
    ),
    path(
        (
            r'v1/devices/<str:device_library_id>/'
            r'registrations/<str:pass_type_id>'
        ),
        views.RegistrationsViewSet.as_view(),
        name='registrations',
    ),

    path(
        r'v1/passes/<str:pass_type_id>/<str:serial_number>',
        views.LatestVersionViewSet.as_view(),
        name='latest_version',
    ),
    path(
        r'v1/log',
        views.LogViewSet.as_view(),
        name='log',
    ),

    path(
        r'test/',
        views.TestViewSet.as_view(),
        name='test',
    ),
]
