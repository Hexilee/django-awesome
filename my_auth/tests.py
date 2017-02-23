from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
import datetime
import hashlib
# Create your tests here.
from .views import token_generator
from .models import Users, Tokens
from .middlewares import BasicMiddleware, AuthMiddleware
from django_awesome.settings import EXPIRE_TIME, TOKEN_NAME


class UsersAndTokensModelsTest(TestCase):
    def test_user_and_token(self):
        test_email = 'name@example.com'
        token = Tokens(created_at=timezone.now(),
                       expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
                       user_email=test_email,
                       value=token_generator('password'))
        token.save()

        Users.objects.create(name='name', email=test_email, password='password', created_at=timezone.now(),
                             image='https://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(
                                 test_email.encode('utf-8')).hexdigest(),
                             current_token=token)
        test1_token = Tokens.objects.get(user_email=test_email)
        test1_user = Users.objects.get(email=test_email)
        self.assertEqual(test1_token, token)
        self.assertEqual(test1_user.current_token, token)


# test objects for BasicMiddlewareTest #################################################################################


def test_function(request):
    return HttpResponse('Hello')


class TestRequestMiddleware(BasicMiddleware):
    def process_request(self, request):
        request.test_attr = 'Hello'


class TestResponseMiddleware(BasicMiddleware):
    def process_response(self, request, response):
        response.content = response.content + b' ' + request.test_attr.encode('utf-8')
        return response


# test objects end #####################################################################################################

class BasicMiddlewareTest(TestCase):
    def test_inputted_handler_function(self):
        test1_request = HttpRequest()
        test1_request.test_attr = 'World'
        # if test_function is callable
        test_basic_middleware1 = BasicMiddleware(test_function)
        self.assertEqual(test_basic_middleware1(test1_request).content, b'Hello')
        # if not test_function is callable
        test_basic_middleware2 = BasicMiddleware(str())
        self.assertEqual(test_basic_middleware2(test1_request), None)

    def test_process_request_function(self):
        test2_request = HttpRequest()
        test2_request.test_attr = 'World'
        test_request_middleware = TestRequestMiddleware(test_function)
        self.assertEqual(hasattr(test_request_middleware, 'process_request'), True)

        processed_response = test_request_middleware(test2_request)

        self.assertEqual(test2_request.test_attr, 'Hello')
        self.assertEqual(processed_response.content, b'Hello')

    def test_process_response_function(self):
        test3_request = HttpRequest()
        test3_request.test_attr = 'World'
        test_response_middleware = TestResponseMiddleware(test_function)
        processed_response = test_response_middleware(test3_request)
        self.assertEqual(processed_response.content, b'Hello World')


# test objects for AuthMiddlewareTest ##################################################################################
def test_email(num):
    return 'test%d@example.com' % num


def test_generate_new_user(token, email_num):
    return Users(name='Test', email=test_email(email_num), password='test', created_at=timezone.now(),
                 image='test@test.com/7a8d78sd87as?', current_token=token)


class TestAuthHttpRequest(HttpRequest):
    def __init__(self, *args, **kwargs):
        self.cookies = dict()
        self.__user__ = None
        self.auth_error = None
        super(TestAuthHttpRequest, self).__init__()


test_auth_middleware = AuthMiddleware(test_function)


# test objects end #####################################################################################################
class AuthMiddlewareTest(TestCase):
    def auth_middleware_output_test1(self):
        # test1, has no token
        test1_token = Tokens(created_at=timezone.now(),
                             expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
                             user_email=test_email(1),
                             value=token_generator('password1'))
        test1_token.save()

        test1_user = test_generate_new_user(test1_token, 1)
        test1_user.save()

        request1 = TestAuthHttpRequest()
        test_auth_middleware(request1)

        self.assertEqual(request1.__user__, None)
        self.assertEqual(request1.auth_error, '你还没登录呢~请登录')

    def auth_middleware_output_test2(self):
        # test2, token is invalid
        test2_token = Tokens(created_at=timezone.now(),
                             expire_at=timezone.now() + datetime.timedelta(hours=EXPIRE_TIME),
                             user_email=test_email(2),
                             value=token_generator('password2'))
        test2_token.save()

        test2_user = test_generate_new_user(test2_token, 2)
        test2_user.save()

        request2 = TestAuthHttpRequest()
        request2.cookies[TOKEN_NAME] = token_generator('password1')
        test_auth_middleware(request2)

        self.assertEqual(request2.__user__, None)
        self.assertEqual(request2.auth_error, '登录已过期，请重新登录!')

    def auth_middleware_output_test3(self):
        # test3, token is expired
        test3_token = Tokens(created_at=timezone.now() - datetime.timedelta(hours=EXPIRE_TIME),
                             expire_at=timezone.now() - datetime.timedelta(seconds=1),
                             user_email=test_email(3),
                             value=token_generator('password3'))
        test3_token.save()

        test3_user = test_generate_new_user(test3_token, 3)
        test3_user.save()

        request3 = TestAuthHttpRequest()
        request3.cookies[TOKEN_NAME] = test3_token.value
        test_auth_middleware(request3)

        self.assertEqual(request3.__user__, None)
        self.assertEqual(request3.auth_error, '登录已过期，请重新登录')



class LoginViewTest(TestCase):
    def test_login_status_code(self):
        pass


class RegisterViewTest(TestCase):
    def test_Register_status_code(self):
        pass
