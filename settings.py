import os
import sys

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


BASE_DIR = os.path.dirname(__file__)

SYNC_TIMEOUT = 10
DATABASE = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
    'database': os.environ.get('POSTGRES_DB', 'auto_collector'),
    'user': os.environ.get('POSTGRES_USER', 'auto_collector'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'auto_collector'),
}

if 'DATABASE_URL' in os.environ:
    url = urlparse(os.environ['DATABASE_URL'])

    DATABASE = {
        'host': url.hostname,
        'port': url.port,
        'database': url.path[1:],
        'user': url.username,
        'password': url.password,
    }

SITE_ADDR = '0.0.0.0'
SITE_PORT = os.environ.get('PORT', 80)

TEMPLATE_DIR = os.path.join(BASE_DIR, 'auto', 'templates')
STATIC_URL = 'http://127.0.0.1:8081/'

SHORTENER_API_URL = 'https://www.googleapis.com/urlshortener/v1/url'
SHORTENER_API_KEY = ''
SHORTENER_MAX_REQUESTS_PER_SECOND = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log')
        },
    },
    'loggers': {
        'auto': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

try:
    from settings_local import *
except ImportError as e:
    print(e)
