from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime
import hashlib
import time
# Create your tests here.
from django_awesome.settings import EXPIRE_TIME
from .models import auth, Blogs, Comments
from .templatetags.blog_filter import datetime_filter
from .utilities import Page, get_page_index


class BlogsAndCommentsModelsTest(TestCase):
    def test_blogs_comments_models(self):
        test_content = 'have a test!'
        test_summary = 'try your best'
        test_email = 'name@example.com'

        token = auth.models.Tokens(created_at=timezone.now(),
                                   expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
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
    def test_index_status_code(self):
        pass


class BlogViewTest(TestCase):
    def test_blog_status_code(self):
        pass


class BlogListViewTest(TestCase):
    def test_blog_list_status_code(self):
        pass


# test objects for DatetimeFilterTest ##################################################################################
def test_raw_time_generator(test_second):
    raw_time_now = int(time.time())
    return raw_time_now - test_second


def test_differ_seconds_now_from_then(time_then):
    return int(time.time()) - time_then


# test objects end #####################################################################################################


class TemplatetagsDatetimeFilterTest(TestCase):
    def test_templatetags_datetime_filter(self):
        test1_raw_time = test_raw_time_generator(30)
        self.assertEqual(datetime_filter(test1_raw_time), u'1分钟前')

        test2_raw_time = test_raw_time_generator(1000)
        self.assertEqual(datetime_filter(test2_raw_time),
                         u'%s分钟前' % (test_differ_seconds_now_from_then(test2_raw_time) // 60))

        test3_raw_time = test_raw_time_generator(10000)
        self.assertEqual(datetime_filter(test3_raw_time),
                         u'%s小时前' % (test_differ_seconds_now_from_then(test3_raw_time) // 3600))

        test4_raw_time = test_raw_time_generator(100000)
        self.assertEqual(datetime_filter(test4_raw_time),
                         u'%s天前' % (test_differ_seconds_now_from_then(test4_raw_time) // 86400))

        test5_raw_time = test_raw_time_generator(1000000)
        dt = datetime.datetime.fromtimestamp(test5_raw_time)
        self.assertEqual(datetime_filter(test5_raw_time),
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
