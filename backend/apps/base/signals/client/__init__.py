from .bonus import bonus_post_save
from .client import client_post_save
from .reward import reward_post_save
from .stamp import stamp_post_save
from .transaction import transaction_post_save

__all__ = (
    'bonus_post_save',
    'client_post_save',
    'reward_post_save',
    'stamp_post_save',
    'transaction_post_save',
)
