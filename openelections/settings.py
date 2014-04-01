from django.conf import settings
import os, sys

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
# Find templates in the same folder as settings.py.
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_PATH, 'templates'),
)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Peter Doyle', 'peter@elections.stanford.edu'),
    ('Robin Woodby', 'rwoodby@stanford.edu'),
)

MANAGERS = ADMINS

WSGI_APPLICATION = "openelections.wsgi.application"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = ''

# Make this unique, and don't share it with anybody.
#SECRET_KEY = 'qszo%3la9zL+2Jv96hA)6*87e$thpjibn0il$@2Fk$tqp&5)lv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
#    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'webauth.middleware.WebauthMiddleware',
)

ROOT_URLCONF = 'openelections.urls'

#TEMPLATE_DIRS = (
#    '/home/admin-elections/elections/openelection/openelections/templates/',
#)

FIXTURE_DIRS = ('fixtures/',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.staticfiles',
    'issues',
    'petitions',
    #'webauth',
    'ballot',
    'webauth',
    'gunicorn',
)

#APPEND_SLASH = False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#WEBAUTH_SHARED_SECRET = 'a2d24bf589b1dea3d83f317019e2ff83bf430b8d1c2a3f741dbf7d72f196d8cf6a6d113de356dc77'
#WEBAUTH_URL = 'https://www.stanford.edu/~trusheim/cgi-bin/wa-authenticate-test.php'

STUDENT_CSV = '' # FILL ME!
