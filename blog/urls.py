from django.conf.urls import url
from . import views
from . import apis

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<blog_id>[0-9]+)/$', views.blog, name='blog'),
    url(r'^getList/$', apis.api_blog_list, name='blog_list'),
]