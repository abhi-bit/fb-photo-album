from snaptest.snap.models import Snap
from urllib2 import urlopen

from djcelery import celery

@celery.task
def get_fb_photo(i):
    album_name = Snap.objects.all()[0].values().get("album_info_name")
    graph_url_id = "https://127.0.0.1:8000/get-photo/?album_name=%s" % (album_name)
    urlopen(graph_url_id).read()
    sleep(i)
    return i
