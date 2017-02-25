from django.conf.urls import url
from . import views
from . import apis

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<blog_id>[0-9]+)/$', views.get_blog, name='blog'),
    url(r'^getList/$', apis.api_blog_list, name='blog_list'),
    url(r'^api/(?P<comment_id>[0-9]+)/comments/$', apis.api_blog_comments, name='blog_comments'),
    url(r'^(?P<comment_id>[0-9]+)/comments/delete/$', apis.api_comments_delete, name='comments_delete')
]