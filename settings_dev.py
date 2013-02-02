from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'openelections_dev',
        'USER': 'dev_user',
        'PASSWORD': 'hello1'
    }
}

MEDIA_ROOT = '/home/daniel/openelections/public/media'
BALLOT_ROOT = '/home/daniel/openelections/ballots'
LOG_ROOT = '/home/daniel/openelections/logs'
STUDENT_CSV = '/home/daniel/openelections/students.csv'


WEBAUTH_SHARED_SECRET = 'test'
WEBAUTH_URL = 'https://www.stanford.edu/~holstein/cgi-bin/Django-WebAuth/webauth-host/wa-authenticate-test.php'

BASE_URL = 'http://localhost:8000/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = BASE_URL + 'media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.                                                               
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = BASE_URL + 'media/admin/'
