from django.conf.urls import url
from . import views
from . import apis

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^blog/$', views.index, name='list'),
    url(r'^blog/(?P<blog_id>[0-9]+)/$', views.get_blog, name='blog'),
    url(r'^blog/getList/$', apis.api_blog_list, name='blog_list'),
    url(r'^blog/api/(?P<blog_id>[0-9]+)/comments/$', apis.api_blog_comments, name='blog_comments'),
    url(r'^blog/(?P<comment_id>[0-9]+)/comments/delete/$', apis.api_comments_delete, name='comments_delete')
]
