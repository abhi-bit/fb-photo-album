import BaseHTTPServer
import cookielib
import httplib
import anyjson as json
import random
import mimetypes
import os
import os.path
import stat
import time
import types
import urllib
import webbrowser
import StringIO
import six
from six import b
import datetime
import io

from urlparse import urlparse
from pprint import pprint

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

if six.PY3:
    from urllib.request import build_opener
    from urllib.request import HTTPCookieProcessor
    from urllib.request import BaseHandler
    from urllib.request import HTTPHandler
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.parse import urlencode
    from urllib.error import HTTPError
else:
    from urllib2 import build_opener
    from urllib2 import HTTPCookieProcessor
    from urllib2 import BaseHandler
    from urllib2 import HTTPHandler
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import Request
    from urllib import urlencode

from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Template, Context
from django.http import Http404, HttpResponse
#from mysite.books.models import Book
from django.http import HttpResponseRedirect
from django import forms

from snap.models import Snap, Login, AlbumList

from snap import tasks

APP_ID = '140632262766677'
SERVER_PORT = 8080
ACCESS_TOKEN = None
ACCESS_TOKEN_FILE = '.fb_access_token'
AUTH_SCOPE = ['user_photos', 'email', 'friends_photos', 'friends_about_me' ]
IMAGE_URL_LIST = []
APP_AUTH_INFO = '.app_auth_timestamp'
ALBUM_LIST = []
IMAGE_DATA= '.img_data'

AUTH_SUCCESS_HTML = """
You have successfully logged in to facebook. You can close this window now.
"""

class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global ACCESS_TOKEN

        params = parse_qs(urlparse(self.path).query)
        ACCESS_TOKEN = params.get('access_token', [None])[0]
        if ACCESS_TOKEN:
            data = {'scope': AUTH_SCOPE,
                    'access_token': ACCESS_TOKEN}
            expiration = params.get('expires_in', [None])[0]
            if expiration:
                if expiration == '0':
                    # this is what's returned when offline_access is requested
                    data['expires_at'] = 'never'
                else:
                    data['expires_at'] = int(time.time()+int(expiration))
            open(ACCESS_TOKEN_FILE,'w').write(json.dumps(data))
            self.wfile.write(b(AUTH_SUCCESS_HTML))
        else:
            self.wfile.write(b('<html><head>' '<script>location = "?"+location.hash.slice(1);</script>' '</head></html>'))

def authenticate(request):
    global ACCESS_TOKEN
    needs_auth = True

    if os.path.exists(ACCESS_TOKEN_FILE):
        data = json.loads(open(ACCESS_TOKEN_FILE).read())
        expires_at = data.get('expires_at')
        still_valid = expires_at and (expires_at == 'never' or expires_at > time.time())
        if still_valid and set(data['scope']).issuperset(AUTH_SCOPE):
            ACCESS_TOKEN = data['access_token']
            needs_auth = False

    if needs_auth:
        webbrowser.open(oauth_url(APP_ID, 'http://127.0.0.1:%s/' % SERVER_PORT, AUTH_SCOPE))

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', SERVER_PORT), _RequestHandler)
        while ACCESS_TOKEN is None:
            httpd.handle_request()

    return HttpResponse('You have been autheticated. Auth token being %s' % json.loads(open(ACCESS_TOKEN_FILE).read()).get('access_token'))

def oauth_url(app_id, redirect_uri, auth_scope):
    return 'https://www.facebook.com/dialog/oauth?' + urlencode({'client_id':app_id, 'redirect_uri':redirect_uri, 'response_type':'token', 'scope':','.join(auth_scope)})

def get_photo(request):
    error = False
    if 'album_name' in request.GET:
        album_name = request.GET['album_name']
        if not album_name:
            error = True
        elif len(album_name) > 30:
            error = True
        else:
            token = json.loads(open(ACCESS_TOKEN_FILE).read()).get('access_token')
            graph_url_id = "https://graph.facebook.com/me?&access_token=%s" % (token)
            id = json.loads(urlopen(graph_url_id).read()).get('id')
            user_id = id

            if (Login.objects.filter(fb_user_id__icontains=id)):
                pass
            else:
                p = Login(fb_user_id=id, login_timestamp=int(time.mktime(time.localtime())))
                p.save()

            started_at = Login.objects.get(fb_user_id__icontains=id).login_timestamp
            if ( int(time.mktime(time.localtime())) - int(started_at) ) <= 3600 and len(Snap.objects.filter(album_info_name__icontains=album_name)) <= 12:
                token = json.loads(open(ACCESS_TOKEN_FILE).read()).get('access_token')
                graph_url_album = 'https://graph.facebook.com/me/albums?fields=id,name,updated_time,count&access_token=%s' % (token)
                url_data = json.loads(urlopen(graph_url_album).read())

                for x in xrange(len(url_data.get('data'))):
                    if not AlbumList.objects.filter(fb_album_name__icontains=album_name):
                        AlbumList.objects.create(fb_album_name=url_data.get('data')[x].get('name'), fb_album_id=url_data.get('data')[x].get('id'))

                p = AlbumList.objects.filter(fb_album_name__icontains=album_name).values()
                id = p[0].get('fb_album_id')

                graph_url_photo = 'https://graph.facebook.com/%s/photos?access_token=%s' % (id, token)
                album_data = json.loads(urlopen(graph_url_photo).read())

                URL_LIST = []

                for x in Snap.objects.filter(album_info_name__icontains=album_name):
                    URL_LIST.append(x.url)

                for x in xrange(len(album_data.get('data'))):
                    if album_data.get('data')[x].get('images')[0].get('source') not in URL_LIST:
                        Snap.objects.create(album_info_name=album_name, url=album_data.get('data')[x].get('images')[0].get('source'))
                        if len(Snap.objects.all()) >= 12:
                            break

            else:
                token = json.loads(open(ACCESS_TOKEN_FILE).read()).get('access_token')
                graph_url_email = 'https://graph.facebook.com/me?fields=id,name,email&access_token=%s' % (token)
                email = json.loads(urlopen(graph_url_email).read()).get('email')

                if ( int(time.mktime(time.localtime())) - int(started_at) ) >= 3600:
                    send_mail(
                            'Album created',
                            '1hr has passed since the app was started',
                            'singhabhishek.bit@gmail.com',
                            [email]
                            )
                    return HttpResponse('1hr has passed since the app was started, Mailing the album')
                else:
                    send_mail(
                             'Album created',
                             '12 pics have been added to your album',
                             'singhabhishek.bit@gmail.com',
                             [email]
                             )
                    return HttpResponse('12 pics have been added to your album. Mailing that')


        IMAGE_URL_LIST = []
        for p in Snap.objects.filter(album_info_name__icontains=album_name):
            IMAGE_URL_LIST.append(p.url)
        tasks.get_fb_photo.delay(600)
        return render_to_response('search_results.html', {'IMAGE_URL_LIST': IMAGE_URL_LIST, 'album_name': album_name})

    return render_to_response('search_form.html', {'error': error})

def logout(request):
    token = json.loads(open(ACCESS_TOKEN_FILE).read()).get('access_token')
    graph_url_id = "https://graph.facebook.com/me?&access_token=%s" % (token)
    id = json.loads(urlopen(graph_url_id).read()).get('id')

    p = Login.objects.get(fb_user_id=id)
    p.delete()

    for i in Snap.objects.all():
        i.delete()

    for i in AlbumList.objects.all():
        i.delete()

    if os.path.exists(ACCESS_TOKEN_FILE):
        os.remove(ACCESS_TOKEN_FILE)

    return HttpResponse("Cleared up auth token and db details")


