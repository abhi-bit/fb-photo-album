from tastypie.resources import ModelResource
from snaptest.snap.models import Snap

class SnapEntry(ModelResource):
    class Meta:
        queryset = Snap.objects.all()
        resource_name = 'snap'
        print queryset
