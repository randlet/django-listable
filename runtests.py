import os
import sys
from optparse import OptionParser
sys.path.append("listable-demo")
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

        STATIC_URL = '/static/',
        TEMPLATE_LOADERS=(
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.filesystem.Loader',
            # 'django.template.loaders.eggs.Loader',
        ),

        TEMPLATE_DIRS = (
            os.path.join("listable-demo", "listable_demo", 'templates'),
            os.path.join("listable-demo", "staff", 'templates'),
        ),
        LISTABLE_PAGINATE_BY=10,
        FIXTURE_DIRS=("listable-demo",),
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
