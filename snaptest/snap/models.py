from django.db import models

from tastypie.utils.timezone import now
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Login(models.Model):
    fb_user_id = models.CharField(max_length=20)
    login_timestamp = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s %s' % (self.fb_user_id, self.login_timestamp)

class Snap(models.Model):
    album_info_name = models.CharField(max_length=50)
    url = models.CharField(max_length=500)
    #fetched_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u'%s %s' % (self.album_info_name, self.url)

class AlbumList(models.Model):
    fb_album_name = models.CharField(max_length=50)
    fb_album_id = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s %s' % (self.fb_album_name, self.fb_album_id)
