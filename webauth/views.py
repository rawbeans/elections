from django.http import HttpResponseRedirect, HttpResponse
import urllib2
import settings
from services import WebauthLogin, WebauthLogout, WebauthVersionNotSupported
from django.utils.datastructures import MultiValueDictKeyError

def login(request):
    if not 'WA_user' in request.GET:
        url = request.build_absolute_uri()
        if '?' not in url:
            url += '?'
        url = urllib2.quote(url)
        return HttpResponseRedirect(settings.WEBAUTH_URL + "?from=" + url)
    else:
        try:
            username_64 = request.GET['WA_user'].strip()
            actual_hash = request.GET['WA_hash'].strip()
            name_64 = request.GET['WA_name'].strip()
            version = request.GET['WA_prot'].strip()
        except MultiValueDictKeyError:
            username_64 = ""
            actual_hash = ""
            name_64 = ""
            version = ""

        username = urllib2.base64.b64decode(username_64).strip()
        name = urllib2.base64.b64decode(name_64).strip()
        
        try:
            could_login = WebauthLogin(request,version,username,actual_hash,name)
        except WebauthVersionNotSupported:
            could_login = False
            
        if could_login:
            try:
                next = request.GET['next']
                if next[0] == '/':
                    next = next[1:]
            except MultiValueDictKeyError:
                next = ""
            return HttpResponseRedirect(settings.BASE_URL + next)
        else:
            return HttpResponse("authentication error")

def logout(request):
    WebauthLogout(request)
    return HttpResponseRedirect('/')

def whoami(request):
    return HttpResponse("You are logged in as %s" % request.user.username)