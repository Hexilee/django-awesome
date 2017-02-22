from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime
import hashlib
# Create your tests here.
from django_awesome.settings import EXPIRE_TIME
from .models import auth, Blogs, Comments


class BlogsAndCommentsModelsTest(TestCase):
    def test_blogs_comments_models(self):
        test_content = 'have a test!'
        test_summary = 'try your best'
        test_email = 'name@example.com'

        token = auth.models.Tokens(created_at=timezone.now(),
                                   expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
                                   user_email=test_email,
                                   cookie='cookie')
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
