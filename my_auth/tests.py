from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime
import hashlib
# Create your tests here.
from .views import cookie_generator
from .models import Users, Tokens
from django_awesome.settings import EXPIRE_TIME


class UsersAndTokensModelsTest(TestCase):
    def test_user_and_token(self):
        test_email = 'name@example.com'
        token = Tokens(created_at=timezone.now(),
                       expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
                       user_email=test_email,
                       cookie=cookie_generator('password'))
        token.save()

        Users.objects.create(name='name', email=test_email, password='password', created_at=timezone.now(),
                             image='https://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(
                                 test_email.encode('utf-8')).hexdigest(),
                             current_token=token)
        test1_token = Tokens.objects.get(user_email=test_email)
        test1_user = Users.objects.get(email=test_email)
        self.assertEqual(test1_token, token)
        self.assertEqual(test1_user.current_token, token)


class LoginViewTest(TestCase):
    def test_login_status_code(self):
        pass


class RegisterViewTest(TestCase):
    def test_Register_status_code(self):
        pass
