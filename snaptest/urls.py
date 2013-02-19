from django.conf.urls import *
from django.conf import settings
from snaptest import views
from snaptest.snap.api import SnapEntry

#print dir(views)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

snap_entry = SnapEntry()

urlpatterns = patterns('',
    (r'^auth/$', views.authenticate),
    (r'^logout/$', views.logout),
    (r'^get-photo/$', views.get_photo),
    #(r'^display-photo/$', views.display_photo),
    #(r'^display-photo-ds/$', views.display_photo_ds),
    (r'^api/', include(snap_entry.urls)),
    # Examples:
    # url(r'^$', 'snaptest.views.home', name='home'),
    # url(r'^snaptest/', include('snaptest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
