from settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'elections_db',
        'USER': 'mysql_user',
        'PASSWORD': '398hudb4s{}DSg'
    }
}

MEDIA_ROOT = '/home/admin-elections/elections/media'
BALLOT_ROOT = '/home/admin-elections/elections/ballots'
LOG_ROOT = '/home/admin-elections/elections/logs'
STUDENT_CSV = '/home/admin-elections/elections/students.csv'


WEBAUTH_SHARED_SECRET = 'abcdchangeme'
WEBAUTH_URL = 'https://www.stanford.edu/~rwoodby/cgi-bin/Django-WebAuth/webauth-host/wa-authenticate.php'

BASE_URL = 'http://petitions.stanford.edu/' #173.230.149.189 #petitions.stanford.edu

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = BASE_URL + 'media/'
STATIC_URL = BASE_URL + 'static/'
STATIC_ROOT = '/home/admin-elections/elections/static'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.                                                               
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = BASE_URL + 'media/admin/'
