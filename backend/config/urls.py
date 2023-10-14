from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/', include('apps.api.urls', namespace='api')),
    path(r'passbook/', include('apps.passbook.urls', namespace='passbook')),
    path(r'ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT)
