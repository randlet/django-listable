import os
import sys
from optparse import OptionParser
sys.path.append("listable_demo")
import django

try:
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
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
        LANGUAGE_CODE="en",

        STATIC_URL='/static/',
        #TEMPLATE_LOADERS=(
        #    'django.template.loaders.app_directories.Loader',
        #    'django.template.loaders.filesystem.Loader',
        #    # 'django.template.loaders.eggs.Loader',
        #),
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware'
        ],

        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [
                    os.path.join("listable_demo", "listable_demo", 'templates'),
                    os.path.join("listable_demo", "staff", 'templates'),
                ],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                        # list if you haven't customized them:
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
        FIXTURE_DIRS=("listable_demo",),
        SITE_ID=1,
        NOSE_ARGS=['-s', '--with-coverage', '--cover-package=listable'],
    )

    from django_nose import NoseTestSuiteRunner
except ImportError as e:
    raise ImportError("Missing import:\n%s\n To fix this error, run: pip install -r requirements/test.txt" % e)



def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    run_tests(*args)
