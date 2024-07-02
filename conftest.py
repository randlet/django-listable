import os
import sys
sys.path.append("listable-demo")

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    USE_DEPRECATED_PYTZ=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    ROOT_URLCONF="tests.urls",
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        'django.contrib.messages',
        "django.contrib.sites",
        'django.contrib.staticfiles',
        'django.contrib.admin',
        "listable",
        "staff",
    ],
    MIDDLEWARE=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    LANGUAGE_CODE="en",
    TIME_ZONE = 'America/Toronto',
    STATIC_URL='/static/',

    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join("listable-demo", "listable_demo", 'templates'),
                os.path.join("listable-demo", "listable_demo", "staff", 'templates'),
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.request',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    LISTABLE_PAGINATE_BY=10,
    FIXTURE_DIRS=("listable-demo",),
    SITE_ID=1,
    SECRET_KEY="abc",
)
django.setup()
