import hashlib
from django.conf import settings
from models import WebauthUser
from django.contrib.auth.models import User

WEBAUTH_VERSION = "WA_1"

class WebauthVersionNotSupported(Exception):
    pass

def _make_hash(string):
    m = hashlib.sha1()
    m.update(string)
    return m.hexdigest()

def WebauthLogin(request,version,username,hashString,full_name=None):
    if version != WEBAUTH_VERSION:
        raise WebauthVersionNotSupported

    (nonce,hash) = hashString.split('$')
    expected_hash = _make_hash(settings.WEBAUTH_SHARED_SECRET + nonce + username)

    #print "%s / %s :: %s : %s" % (username,nonce,expected_hash,hash)

    if expected_hash == hash:
        if not WebauthUser.objects.filter(username__exact=username).exists():
            authuser_obj = User.objects.filter(username__exact=username)
            if not authuser_obj.exists():
                user = WebauthUser()
                user.new_webauth(username,full_name)
            else:
                user = authuser_obj.get()
                user.__class__ = WebauthUser
                user.new_webauth(username,full_name)

        request.session['wa_username'] = username
        return True
    else:
        return False

def WebauthLogout(request):
    del request.session['wa_username']