from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(
    r'audiences',
    views.AudienceViewSet,
    basename='audiences'
)
router.register(
    r'certs',
    views.CertViewSet,
    basename='certs'
)
router.register(
    r'client/transactions',
    views.ClientTransactionViewSet,
    basename='client_transactions'
)
router.register(
    r'clients',
    views.ClientViewSet,
    basename='clients'
)
router.register(
    r'employees',
    views.EmployeeViewSet,
    basename='employees'
)
router.register(
    r'reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router.register(
    r'statuses',
    views.StatusViewSet,
    basename='statuses'
)
router.register(
    r'triggers',
    views.TriggerViewSet,
    basename='triggers'
)
router.register(
    r'wallets',
    views.WalletViewSet,
    basename='wallets'
)
router.register(
    r'product/categories',
    views.ProductCategoryViewSet,
    basename='product_categories'
)
router.register(
    r'products',
    views.ProductViewSet,
    basename='products'
)
router.register(
    r'service/categories',
    views.ServiceCategoryViewSet,
    basename='service_categories'
)
router.register(
    r'services',
    views.ServiceViewSet,
    basename='services'
)
router.register(
    r'push',
    views.PushViewSet,
    basename='push'
)
router.register(
    r'transactions',
    views.PartnerTransactionViewSet,
    basename='transactions'
)

urlpatterns = [
    path(
        r'auth/token/',
        views.ObtainAuthTokenViewSet.as_view(),
        name='token'
    ),
    path(
        r'auth/logout/',
        views.LogoutViewSet.as_view(),
        name='logout'
    ),
    path(
        r'user/',
        views.UserViewSet.as_view(),
        name='user'
    ),

    path(
        r'dashboard/',
        views.DashboardViewSet.as_view(),
        name='dashboard'
    ),

    path(
        r'contract/',
        views.ContractViewSet.as_view(),
        name='contract'
    ),

    path(
        r'connect/<uuid:uuid>/verification/',
        views.ConnectVerificationViewSet.as_view(),
        name='connect_verification'
    ),
    path(
        r'connect/<uuid:uuid>/',
        views.ConnectViewSet.as_view(),
        name='connect'
    ),

    path(r'', include(router.urls)),
]
