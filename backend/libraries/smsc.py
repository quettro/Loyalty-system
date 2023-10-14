import re

import requests
from django.conf import settings


class SmsC:
    __phone = None
    __route = 'https://smsc.ru/sys/send.php'

    def __init__(self, username=None, password=None):
        self.__username = username or settings.API_SMSC_USERNAME
        self.__password = password or settings.API_SMSC_PASSWORD

    def set_phone(self, phone):
        msg = 'Номер телефона необходимо передавать в формате: 7XXXXXXXXXX'
        assert re.match(r'^7([0-9]{10})$', phone), msg
        self.__phone = phone

    def call(self):
        assert self.__phone is not None, 'Установите номер телефона.'

        try:
            _params = self.__params({'mes': 'code', 'call': 1, 'fmt': 3})
            _response = requests.get(self.__route, params=_params)
            _json = _response.json()

            if 'error' in _json:
                raise Exception(
                    'Произошла ошибка №{} - {}' . format(
                        _json.get('error_code'),
                        _json.get('error')
                    )
                )
            else:
                if 'id' not in _json or 'code' not in _json:
                    raise Exception(
                        'Не удалось определить ID или код. {}' . format(
                            _response.text()
                        )
                    )
        except Exception as e:
            raise Exception(str(e))

        return _json

    def __params(self, params={}):
        return {**{
            'login': self.__username,
            'psw': self.__password,
            'phones': self.__phone,
        }, **params}
