from os import environ
from pathlib import Path

from django.utils import timezone
from dotenv import load_dotenv
from libraries.passbook import BarcodeFormat

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get('SECRET_KEY')

DEBUG = int(environ.get('DEBUG', default=0))

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS').split()

INSTALLED_APPS = [
    'ckeditor',
    'ckeditor_uploader',
    'prettyjson',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'apps.api',
    'apps.base',
    'apps.users',
    'apps.passbook',
    'apps.documents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': environ.get('MYSQL_DATABASE'),
        'USER': environ.get('MYSQL_USER'),
        'PASSWORD': environ.get('MYSQL_PASSWORD'),
        'HOST': environ.get('MYSQL_HOST'),
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.api.authentication.BearerAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': (
        'apps.api.pagination.CustomPageNumberPagination'
    ),
    'PAGE_SIZE': 2
}

CORS_ALLOWED_ORIGINS = environ.get('CORS_ALLOWED_ORIGINS').split()
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_CREDENTIALS = True

if CORS_ALLOWED_ORIGINS[0] == '*':
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOW_ALL_ORIGINS = True

# Какие виды баркодов можно выбрать при создании карт.
BARCODES = (BarcodeFormat.QR, BarcodeFormat.PDF417,)

# Полный путь к файлу wwdr.pem
WWDR_ROOT = BASE_DIR / 'storage' / 'ios' / 'wwdr.pem'

# Таймаут между отправками верификации звонком.
PHONE_VERIFICATION_TIMEOUT = timezone.timedelta(minutes=1)

# [.pkpass] Блок `Ваш отзыв`.
# 1. Ссылка, куда необходимо отправить клиента, чтобы оставить отзыв.
# 2. Текстовое сообщение. Что видит пользователь, вместо ссылки.
PKPASS_REVIEW_LINK = environ.get('PKPASS_REVIEW_LINK')
PKPASS_REVIEW_TEXT = environ.get('PKPASS_REVIEW_TEXT')

# [.pkpass] Блок `Эмитент карты`.
# 1. Ссылка, куда необходимо отправить клиента.
# 2. Текстовое сообщение. Что видит пользователь, вместо ссылки.
PKPASS_CARD_ISSUER_LINK = environ.get('PKPASS_CARD_ISSUER_LINK')
PKPASS_CARD_ISSUER_TEXT = environ.get('PKPASS_CARD_ISSUER_TEXT')

# [.pkpass] Куда отправлять запросы для регистрации устройств
# после активации карт.
PKPASS_WEB_SERVICE_DOMAIN = environ.get('PKPASS_WEB_SERVICE_DOMAIN')
PKPASS_WEB_SERVICE_URL = f'https://{PKPASS_WEB_SERVICE_DOMAIN}/passbook/'

# Наименование папки где лежат файлы с расширением .pkpass и полный путь
# к данной папке.
PKPASS_DIRNAME = 'clients'
PKPASS_ROOT = MEDIA_ROOT / PKPASS_DIRNAME

# [.pkpass] Шрифт текста. Текст накладывается поверх фонового изображения.
PKPASS_FONT_FAMILY = BASE_DIR / 'storage' / 'fonts' / 'Nunito-Bold.ttf'

# [.pkpass] Какое сообщение накладывать поверх фонового изображения, если
# карта не обслуживается.
PKPASS_MESSAGE_IF_WALLET_IS_DELETED = 'Карта временно не обслуживается'

# [.pkpass] Какое сообщение накладывать поверх фонового изображения, если
# у клиента тип карты: Чоп-карта и клиент получил награду.
PKPASS_MESSAGE_IF_RECEIVED_REWARD = 'Награда получена'

# Какое максимальное количество наград может получить клиент. Не превышать
# 32767, т.к используется PositiveSmallIntegerField.
MAX_REWARDS = 10000

# Какое максимальное количество штампов может получить клиент. Или какое
# максимальное количество штампов можно указать для получения наград при
# создании чоп-карт.
MAX_STAMPS = 10

# Максимальное количество штампов на одной линий.
MAX_NUMBER_OF_STAMPS_PER_ONE_LINE = 5

# Имя пользователя и пароль от сервиса smsc.ru
API_SMSC_USERNAME = environ.get('API_SMSC_USERNAME')
API_SMSC_PASSWORD = environ.get('API_SMSC_PASSWORD')

# Токен для доступа к API на walletpasses.appspot.com.
# Получить: https://walletpasses.appspot.com/register
API_WALLET_PASSES_TOKEN = environ.get('API_WALLET_PASSES_TOKEN')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} [ {asctime} ] {pathname} -> {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} [ {asctime} ] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'django': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': BASE_DIR / 'storage' / 'loggers' / 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'apps': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,
            'filename': BASE_DIR / 'storage' / 'loggers' / 'apps.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['apps', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

REDIS_HOST = environ.get('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = environ.get('REDIS_PORT', default='6379')

CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CKEDITOR_UPLOAD_PATH = MEDIA_ROOT / 'ckeditor'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'None'
    }
}

def is_show_debug_toolbar_callback(*args, **kwargs):
    return int(environ.get('IS_SHOW_DEBUG_TOOLBAR', default=0))

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar'
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware'
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': is_show_debug_toolbar_callback
    }
