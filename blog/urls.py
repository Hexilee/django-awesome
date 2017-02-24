from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<blog_id>[0-9]+)/$', views.blog, name='blog'),
    url(r'^getList/$', views.api_blog_list, name='blog_list'),
]