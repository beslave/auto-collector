import os.path
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SYNC_TIMEOUT = 10
DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'auto_collector',
    'user': 'postgres',
    'password': 'p0stgres',
}
SITE_ADDR = '0.0.0.0'
SITE_PORT = 8080

TEMPLATE_DIR = os.path.join(BASE_DIR, 'auto', 'templates')
STATIC_URL = '/static'
STATIC_ROOT = os.path.join(BASE_DIR, 'frontend', 'static')

SHORTENER_API_URL = 'https://www.googleapis.com/urlshortener/v1/url'
SHORTENER_API_KEY = ''
SHORTENER_MAX_REQUESTS_PER_SECOND = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
    }
}

try:
    from settings_local import *
except ImportError as e:
    print(e)
