from django.conf.urls import url
from . import apis
from . import views
urlpatterns = [
    url(r'^download/(?P<file_id>\w+)/$', apis.get_file, name='get_file'),
    url(r'^file/$', views.file_upload, name='file'),
    url(r'^upload/file/$', apis.upload_file, name='upload')
]
