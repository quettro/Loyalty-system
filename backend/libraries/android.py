import requests
from django.conf import settings


class WalletPasses:
    """
    WalletPasses - отвечает за отправку PUSH уведомлений на Android.
    """
    __route = 'https://walletpasses.appspot.com/'

    def __init__(self, token=None):
        self.__token = token or settings.API_WALLET_PASSES_TOKEN

    def __headers(self, headers={}):
        return {'Authorization': self.__token, **headers}

    def push(self, pass_type_identifier=None, push_tokens=[]):
        _route = f'{self.__route}api/v1/push'

        return requests.post(_route, headers=self.__headers(), json={
            'passTypeIdentifier': pass_type_identifier,
            'pushTokens': push_tokens,
        })
