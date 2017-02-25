from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpRequest
import datetime
import hashlib
import time
import json
# Create your tests here.
from django_awesome.settings import EXPIRED_TIME
from .models import auth, Blogs, Comments
from .templatetags.blog_filter import datetime_filter
from .utilities import Page, get_page_index
from .views import index, get_blog


class BlogsAndCommentsModelsTest(TestCase):
    def test_blogs_comments_models(self):
        test_content = 'have a test!'
        test_summary = 'try your best'
        test_email = 'name@example.com'

        token = auth.models.Tokens(created_at=timezone.now(),
                                   expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                                   user_email=test_email,
                                   value='cookie')
        token.save()

        user = auth.models.Users(name='name', email=test_email, password='password', created_at=timezone.now(),
                                 image='https://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(
                                     test_email.encode('utf-8')).hexdigest(),
                                 current_token=token)
        user.save()

        blog = Blogs(user=user, name='name', summary=test_summary, content=test_content, created_at=timezone.now())
        blog.save()

        comment = Comments(user=user, blog=blog, content=test_content, created_at=timezone.now())
        comment.save()

        test1_blog = Blogs.objects.get(user__email=test_email)
        test1_comment1 = Comments.objects.get(user__email=test_email)
        test1_comment2 = Comments.objects.get(blog__user__email=test_email)

        self.assertEqual(test1_blog, blog)
        self.assertEqual(test1_comment1, comment)
        self.assertEqual(test1_comment2, comment)


class IndexViewTest(TestCase):
    def test_index_view_1(self):
        # test1, no item
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)

        resp_dict = response.context

        page = json.loads(resp_dict['page'])
        self.assertEqual(page, {'ceiling': 0,
                                'has_next': False,
                                'has_previous': False,
                                'item_count': 0,
                                'offset': 0,
                                'page_count': 0,
                                'page_index': 1,
                                'page_size': 8})

    def test_index_view_2(self):
        # test2, there are items, but no 'page' parm
        # create blogs
        test_token = auth.models.Tokens(created_at=timezone.now(), expired_at=timezone.now(), user_email='email',
                                        value='value')
        test_token.save()
        test_user = auth.models.Users(name='Robot', email='email', password='test', created_at=timezone.now(),
                                      image='image',
                                      current_token=test_token)
        test_user.save()

        for i in range(9):
            Blogs.objects.create(user=test_user, name='test', summary='test', content='test', created_at=timezone.now())
        ############################################################
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)

        resp_dict = response.context

        page = json.loads(resp_dict['page'])
        self.assertEqual(page, {'ceiling': 8,
                                'has_next': True,
                                'has_previous': False,
                                'item_count': 9,
                                'offset': 0,
                                'page_count': 2,
                                'page_index': 1,
                                'page_size': 8})

        # test3, items, 'page' parm
        response = self.client.get(reverse('blog:index') + '?page=2')
        self.assertEqual(response.status_code, 200)

        resp_dict = response.context

        page = json.loads(resp_dict['page'])
        self.assertEqual(page, {'ceiling': 9,
                                'has_next': False,
                                'has_previous': True,
                                'item_count': 9,
                                'offset': 8,
                                'page_count': 2,
                                'page_index': 2,
                                'page_size': 8})


class BlogViewTest(TestCase):
    def test_get_blog_view(self):
        # create blogs
        test_token = auth.models.Tokens(created_at=timezone.now(), expired_at=timezone.now(), user_email='email',
                                        value='value')
        test_token.save()

        test_user = auth.models.Users(name='Robot', email='email', password='test', created_at=timezone.now(),
                                      image='image',
                                      current_token=test_token)
        test_user.save()

        test_blog = Blogs(user=test_user, name='test', summary='test', content='test', created_at=timezone.now())
        test_blog.save()

        # test1, no comment
        response1 = self.client.get(reverse('blog:blog', args=(test_blog.pk, )))
        resp_dict = response1.context
        self.assertEqual(resp_dict['comments'], None)

        # test2, a comment
        test_comment = Comments(user=test_user, blog=test_blog, content='test', created_at=timezone.now())
        test_comment.save()
        response2 = self.client.get(reverse('blog:blog', args=(test_blog.pk, )))
        resp_dict = response2.context
        self.assertEqual(resp_dict['comments'][0], test_comment)


class BlogListViewTest(TestCase):
    def test_blog_list_status_code(self):
        pass


# test objects for DatetimeFilterTest ##################################################################################
def test_date_time_generator(test_second):
    date_time_now = timezone.now()
    return date_time_now - datetime.timedelta(seconds=test_second)


def test_differ_seconds_now_from_then(time_then):
    return int(time.time()) - int(time_then.timestamp())


# test objects end #####################################################################################################


class TemplatetagsDatetimeFilterTest(TestCase):
    def test_templatetags_datetime_filter(self):
        test1_date_time = test_date_time_generator(30)
        self.assertEqual(datetime_filter(test1_date_time), u'1分钟前')

        test2_date_time = test_date_time_generator(1000)
        self.assertEqual(datetime_filter(test2_date_time),
                         u'%s分钟前' % (test_differ_seconds_now_from_then(test2_date_time) // 60))

        test3_date_time = test_date_time_generator(10000)
        self.assertEqual(datetime_filter(test3_date_time),
                         u'%s小时前' % (test_differ_seconds_now_from_then(test3_date_time) // 3600))

        test4_date_time = test_date_time_generator(100000)
        self.assertEqual(datetime_filter(test4_date_time),
                         u'%s天前' % (test_differ_seconds_now_from_then(test4_date_time) // 86400))

        test5_date_time = test_date_time_generator(1000000)
        dt = test5_date_time
        self.assertEqual(datetime_filter(test5_date_time),
                         u'%s年%s月%s日' % (dt.year, dt.month, dt.day))


class TestApisPage(TestCase):
    def test_api_page(self):
        # test 1, page_index < page_count
        p1 = Page(100, 1)
        self.assertEqual(p1.page_count, 13)
        self.assertEqual(p1.offset, 0)
        self.assertEqual(p1.ceiling, 8)

        # test2, page_index > page_count
        p2 = Page(91, 11, 10)
        self.assertEqual(p2.page_count, 10)
        self.assertEqual(p2.offset, 90)
        self.assertEqual(p2.ceiling, 91)
        self.assertEqual(p2.page_index, 10)

        # test3, page_index == page_count
        p3 = Page(91, 10, 10)
        self.assertEqual(p3.page_count, 10)
        self.assertEqual(p3.offset, 90)
        self.assertEqual(p3.ceiling, 91)

        # test4, item_count == 0
        p4 = Page(0, 10, 10)
        self.assertEqual(p4.offset, 0)
        self.assertEqual(p4.ceiling, 0)
        self.assertEqual(p4.page_index, 1)


class TestGetPageIndex(TestCase):
    def test_get_page_index(self):
        # test1, page_str >= 1
        test1_page_index = get_page_index('3')
        self.assertEqual(test1_page_index, 3)

        # test2, page_str < 1
        test2_page_index = get_page_index('-2')
        self.assertEqual(test2_page_index, 1)
