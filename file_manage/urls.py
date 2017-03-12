from django.conf.urls import url
from . import apis
urlpatterns = [
    url(r'^download/(?P<file_id>\w+)/$', apis.get_file, name='get_file'),
]
