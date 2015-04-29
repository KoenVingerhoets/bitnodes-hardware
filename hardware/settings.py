#
# Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import os
import string
from ConfigParser import RawConfigParser
from cStringIO import StringIO
from datetime import timedelta
from psutil import net_if_addrs

from django.utils.crypto import get_random_string

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_CHARS = string.letters + string.digits

SECRET_FILE = os.path.join(BASE_DIR, '.secret_key')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    SECRET_KEY = get_random_string(100, SECRET_CHARS)
    with open(SECRET_FILE, 'w') as f:
        f.write(SECRET_KEY)

DEBUG_FILE = os.path.join(BASE_DIR, '.debug')
DEBUG = os.path.exists(DEBUG_FILE)

SITE_ID = 1

ALLOWED_HOSTS = ['*']

# 2 instances of Gunicorn are launched to serve private (LAN) and public (WAN)
# network. Private network will have access to the administration app to manage
# the device. Public network will only have read-only access to the dashboard
# to view the status of the device.
PRIVATE = os.environ.get('NETWORK', None) == 'private'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'djsupervisor',
    'rest_framework',
    'djcelery',
    'kombu.transport.django',  # Django database transport for Celery
    'debug_toolbar',
    'hardware.administration',
    'hardware.api',
    'hardware.dashboard',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'hardware.middleware.GlobalSettingsMiddleware',
)

ROOT_URLCONF = 'hardware.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'hardware.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'default_cache',
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '2000/day',
    },
}

LOGIN_URL = '/administration/login/'

SUPERVISOR = {
    'NAME': 'hardware',
    'PRIVATE_GUNICORN': {
        'ADDRESS': '127.0.0.1:8000',
    },
    'PUBLIC_GUNICORN': {
        'ADDRESS': '127.0.0.1:9000',
    },
}

BROKER_URL = 'django://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_IGNORE_RESULT = True
CELERY_TASK_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'system-info-task': {
        'task': 'hardware.administration.tasks.system_info_task',
        'schedule': timedelta(minutes=15),
        'relative': True,
    },
}

WEBSOCKET_DAEMON = os.path.join(BASE_DIR, 'poll.py')
WEBSOCKET_HOST = '127.0.0.1'
WEBSOCKET_PORT = 8888

# Network interface connected to the LAN
NETWORK_INTERFACE = 'eth0'
_interfaces = net_if_addrs().keys()
if NETWORK_INTERFACE not in _interfaces:
    NETWORK_INTERFACE = None
    _allowed_interfaces = [
        'eth0',  # Linux
        'en0',  # Mac OS X
    ]
    for interface in _allowed_interfaces:
        if interface in _interfaces:
            NETWORK_INTERFACE = interface
if NETWORK_INTERFACE is None:
    raise Exception('Unable to locate a valid network interface! '
                    'Please set NETWORK_INTERFACE in settings.py manually.')

# Supervisor will not start Bitcoin client if it does not exist
BITCOIND = '/usr/local/bin/bitcoind'
if not os.path.isfile(BITCOIND):
    BITCOIND = None

BITCOIN_DIR = os.path.join(BASE_DIR, '.bitcoin')
SDCARD_DIR = '/media/data'
if os.path.exists(SDCARD_DIR):
    BITCOIN_DIR = os.path.join(SDCARD_DIR, '.bitcoin')

# Execute the following command to create a new bitcoin.conf:
# ./manage.py create_bitcoin_conf
BITCOIN_CONF = os.path.join(BITCOIN_DIR, 'bitcoin.conf')

# Default RPC settings used by create_bitcoin_conf
RPC_HOST = '127.0.0.1'
RPC_PORT = 8332

# rpcuser and rpcpassword are set automatically by create_bitcoin_conf
RPC_USER = None
RPC_PASSWORD = None
if os.path.isfile(BITCOIN_CONF):
    _conf = RawConfigParser()
    _conf.readfp(StringIO('[bitcoind]\n' + open(BITCOIN_CONF, 'r').read()))
    RPC_HOST = _conf.get('bitcoind', 'rpcbind')
    RPC_PORT = _conf.get('bitcoind', 'rpcport')
    RPC_USER = _conf.get('bitcoind', 'rpcuser')
    RPC_PASSWORD = _conf.get('bitcoind', 'rpcpassword')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s (%(funcName)s) %(message)s',
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 2097152,  # 2MB
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'hardware': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}