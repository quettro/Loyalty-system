from .audience import AudienceAdmin
from .cert import CertAdmin
from .city import CityAdmin
from .client import (BonusAdmin, ClientAdmin, ClientTransactionAdmin,
                     IncreasedPercentageAdmin, RewardAdmin, StampAdmin)
from .company import CompanyAdmin
from .employee import EmployeeAdmin
from .partner import PartnerAdmin, PartnerTransactionAdmin, PartnerTypeAdmin
from .permission import PermissionAdmin
from .product import ProductAdmin, ProductCategoryAdmin
from .push import PushAdmin
from .registration import RegistrationAdmin
from .review import ReviewAdmin
from .service import ServiceAdmin, ServiceCategoryAdmin
from .status import StatusAdmin
from .tariff import TariffAdmin
from .trigger import TriggerAdmin
from .verification import VerificationAdmin
from .wallet import WalletAdmin

__all__ = (
    'AudienceAdmin',
    'CertAdmin',
    'CityAdmin',
    'BonusAdmin',
    'ClientAdmin',
    'ClientTransactionAdmin',
    'IncreasedPercentageAdmin',
    'RewardAdmin',
    'StampAdmin',
    'CompanyAdmin',
    'EmployeeAdmin',
    'PartnerAdmin',
    'PartnerTransactionAdmin',
    'PartnerTypeAdmin',
    'PermissionAdmin',
    'ProductAdmin',
    'ProductCategoryAdmin',
    'PushAdmin',
    'RegistrationAdmin',
    'ReviewAdmin',
    'ServiceAdmin',
    'ServiceCategoryAdmin',
    'StatusAdmin',
    'TariffAdmin',
    'TriggerAdmin',
    'VerificationAdmin',
    'WalletAdmin',
)
