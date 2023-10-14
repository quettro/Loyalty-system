import json
import time

import jwt
from hyper import HTTPConnection


class APNsPusher:
    """
    APNsPusher - отвечает за отправку PUSH уведомлений на iOS.
    """
    def __init__(self, apns_key_id, apns_key_path, team_id, bundle_id):
        self.ALGORITHM = 'ES256'
        self.APNS_KEY_ID = apns_key_id
        self.APNS_AUTH_KEY = apns_key_path
        self.TEAM_ID = team_id
        self.BUNDLE_ID = bundle_id

    def push(self, title, body, device_token, is_production):
        with open(self.APNS_AUTH_KEY) as file:
            secret = file.read()

        token = jwt.encode(
            payload={'iss': self.TEAM_ID, 'iat': time.time()},
            key=secret,
            algorithm=self.ALGORITHM,
            headers={'alg': self.ALGORITHM, 'kid': self.APNS_KEY_ID}
        )

        headers = {
            'apns-expiration': '0',
            'apns-priority': '10',
            'apns-topic': self.BUNDLE_ID,
            'authorization': (
                'bearer {0}' . format(token.encode().decode('ascii'))
            )
        }

        if is_production:
            conn = HTTPConnection('api.push.apple.com:443')
        else:
            conn = HTTPConnection('api.development.push.apple.com:443')

        payload = json.dumps({
            'aps': {
                'alert': {
                    'title': title,
                    'body': body
                },
                'badeg': 1,
                'sound': 'default'
            }
        }).encode('utf-8')

        path = '/3/device/{0}'.format(device_token)

        conn.request('POST', path, payload, headers=headers)
        response = conn.get_response()

        if response.status != 200:
            content = response.read().decode('utf-8')
            headers = str(response.headers)

            if not content:
                content = (
                    'Что-то пошло не так, '
                    'не удалось отправить PUSH уведомление.'
                )

            raise Exception(content, headers)

        return response
