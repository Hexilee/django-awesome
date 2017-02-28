from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
import datetime
import hashlib
import json
# Create your tests here.
from .utilites import token_generator, password_generator
from .models import Users, Tokens
from .middlewares import BasicMiddleware, AuthMiddleware
from django_awesome.settings import EXPIRED_TIME, TOKEN_NAME
from .views import register, login, logout


class UsersAndTokensModelsTest(TestCase):
    def test_user_and_token(self):
        test_email = 'name@example.com'
        token = Tokens(created_at=timezone.now(),
                       expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
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
        self.COOKIES = dict()
        self.__user__ = None
        self.auth_error = None
        super(TestAuthHttpRequest, self).__init__()


test_auth_middleware = AuthMiddleware(test_function)


# test objects end #####################################################################################################


class MyAuthMiddlewareTest(TestCase):
    def test_auth_middleware_output_test1(self):
        # test1, has no token
        test1_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(1),
                             value=token_generator('password1'))
        test1_token.save()

        test1_user = test_generate_new_user(test1_token, 1)
        test1_user.save()

        request1 = TestAuthHttpRequest()
        test_auth_middleware(request1)

        self.assertEqual(request1.__user__, None)
        self.assertEqual(request1.auth_error, '你还没登录呢~请登录')

    def test_auth_middleware_output_test2(self):
        # test2, token is invalid
        test2_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(2),
                             value=token_generator('password2'))
        test2_token.save()

        test2_user = test_generate_new_user(test2_token, 2)
        test2_user.save()

        request2 = TestAuthHttpRequest()
        request2.COOKIES[TOKEN_NAME] = token_generator('password1')
        test_auth_middleware(request2)

        self.assertEqual(request2.__user__, None)
        self.assertEqual(request2.auth_error, '登录已过期，请重新登录!')

    def test_auth_middleware_output_test3(self):
        # test3, token is expired
        test3_token = Tokens(created_at=timezone.now() - datetime.timedelta(hours=EXPIRED_TIME),
                             expired_at=timezone.now() - datetime.timedelta(seconds=1),
                             user_email=test_email(3),
                             value=token_generator('password3'))
        test3_token.save()

        test3_user = test_generate_new_user(test3_token, 3)
        test3_user.save()

        request3 = TestAuthHttpRequest()
        request3.COOKIES[TOKEN_NAME] = test3_token.value
        test_auth_middleware(request3)

        self.assertEqual(request3.__user__, None)
        self.assertEqual(request3.auth_error, '登录已过期，请重新登录')

    def test_auth_middleware_output_test4(self):
        # test4, user_email is invalid
        test4_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(3),
                             value=token_generator('password4'))
        test4_token.save()

        test4_user = test_generate_new_user(test4_token, 4)
        test4_user.save()

        request4 = TestAuthHttpRequest()
        request4.COOKIES[TOKEN_NAME] = test4_token.value
        test_auth_middleware(request4)

        self.assertEqual(request4.__user__, None)
        self.assertEqual(request4.auth_error, '此账号不存在或账号邮箱已更改')

    def test_auth_middleware_output_test5(self):
        # test5, user is not active
        test5_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(5),
                             value=token_generator('password5'))
        test5_token.save()

        test5_user = test_generate_new_user(test5_token, 5)
        test5_user.is_active = False
        test5_user.save()

        request5 = TestAuthHttpRequest()
        request5.COOKIES[TOKEN_NAME] = test5_token.value
        test_auth_middleware(request5)

        self.assertEqual(request5.__user__, None)
        self.assertEqual(request5.auth_error, '此账号已经冻结')

    def test_auth_middleware_output_test6(self):
        # test6, user.current_token != token
        test6_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(6),
                             value=token_generator('password6'))
        test6_token.save()
        #
        test6_changed_token = Tokens(created_at=timezone.now(),
                                     expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                                     user_email=test_email(6),
                                     value=token_generator('password6_changed'))
        test6_changed_token.save()  # 不存储则测试报错

        test6_user = test_generate_new_user(test6_changed_token, 6)
        test6_user.save()

        request6 = TestAuthHttpRequest()
        request6.COOKIES[TOKEN_NAME] = test6_token.value
        test_auth_middleware(request6)

        self.assertEqual(request6.__user__, None)
        self.assertEqual(request6.auth_error, '你的账号已在别处登录')

    def test_auth_middleware_output_test7(self):
        # test6, valid user
        test7_token = Tokens(created_at=timezone.now(),
                             expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                             user_email=test_email(7),
                             value=token_generator('password7'))
        test7_token.save()

        test7_user = test_generate_new_user(test7_token, 7)
        test7_user.save()

        request7 = TestAuthHttpRequest()
        request7.COOKIES[TOKEN_NAME] = test7_token.value
        test_auth_middleware(request7)

        self.assertEqual(request7.auth_error, None)
        self.assertEqual(request7.__user__.email, test7_user.email)
        self.assertEqual(request7.__user__.password, '**********')


class LoginViewTest(TestCase):
    def test_login_view_1_2(self):
        # test1, get, no next
        response1 = self.client.get(reverse('auth:login'))
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.context['next'], '/blog/')

        # test2, get, has next
        response2 = self.client.get(reverse('auth:login') + '?next=/blog/10')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.context['next'], '/blog/10')

    def test_login_view_3_8(self):
        # test3, post, no data input
        response3 = self.client.post(reverse('auth:login'))
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(json.loads(response3.content.decode('utf-8')), {'error': '没有数据输入！'})

        # test4, post, invalid email
        test4_data = json.dumps({'email': '3131da@as', 'password': 'e9a14fb4e17114337440905576c363efeb031af3'},
                                ensure_ascii=False)
        response4 = self.client.post(reverse('auth:login'), data=test4_data, content_type='application/json')
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(json.loads(response4.content.decode('utf-8')), {'error': '请输入正确的邮箱格式'})

        # test5, post, invalid password
        test5_data = json.dumps({'email': 'name@qq.com', 'password': '9a14efb4e17114337440905576c'},
                                ensure_ascii=False)
        response5 = self.client.post(reverse('auth:login'), data=test5_data, content_type='application/json')
        self.assertEqual(response5.status_code, 200)
        self.assertEqual(json.loads(response5.content.decode('utf-8')), {'error': '密码加密错误，请刷新重试'})

        # test6, post, invalid user
        test6_data = json.dumps({'email': 'name@qq.com', 'password': '9a14efb4e17114337440905576c363efeb031af3'},
                                ensure_ascii=False)
        response6 = self.client.post(reverse('auth:login'), data=test6_data, content_type='application/json')
        self.assertEqual(response6.status_code, 200)
        self.assertEqual(json.loads(response6.content.decode('utf-8')), {'error': '账号邮箱不存在'})

        # test7, post, wrong password
        new_token = Tokens(
            expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
            value=token_generator('9a14efb4e17114337440905576c363efeb031af3'),
            user_email=test_email(1)
        )
        new_token.save()

        new_user = test_generate_new_user(token=new_token, email_num=1)
        new_user.password = password_generator('9a14efb4e17114337440905576c363efeb031af3')
        new_user.save()

        test7_data = json.dumps({'email': test_email(1), 'password': '7440905576c363efeb031af39a14efb4e1711433'},
                                ensure_ascii=False)
        response7 = self.client.post(reverse('auth:login'), data=test7_data, content_type='application/json')
        self.assertEqual(response7.status_code, 200)
        self.assertEqual(json.loads(response7.content.decode('utf-8')), {'error': '密码错误'})

        # test8, post, right password
        test8_data = json.dumps({'email': test_email(1), 'password': '9a14efb4e17114337440905576c363efeb031af3'},
                                ensure_ascii=False)
        raw_response8 = self.client.post(reverse('auth:login'), data=test8_data, content_type='application/json')

        self.assertEqual(raw_response8.status_code, 200)
        response8 = json.loads(raw_response8.content.decode('utf-8'))

        self.assertEqual(response8[0]['fields']['password'], '***************')


# test_objects for RegisterView #########################################################################################

def test_data_generator(email, password, name):
    return json.dumps(dict(email=email, password=password, name=name), ensure_ascii=False)


# end objects

class RegisterViewTest(TestCase):
    def test_register_view_1_2(self):
        # test1, get, no next
        response1 = self.client.get(reverse('auth:register'))
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.context['next'], '/blog/')
        # test2, get, has next
        response2 = self.client.get(reverse('auth:register') + '?next=/blog/10')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.context['next'], '/blog/10')

    def test_register_view_3_(self):
        # test3, post, no data input
        response3 = self.client.post(reverse('auth:register'))
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(json.loads(response3.content.decode('utf-8')), {'error': '没有数据输入！'})

        # test4, post, invalid email
        response4 = self.client.post(reverse('auth:register'),
                                     data=test_data_generator(email='name@qq',
                                                              password='9a14efb4e17114337440905576c363efeb031af3',
                                                              name='西西'),
                                     content_type='application/json')
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(json.loads(response4.content.decode('utf-8')), {'error': '请输入正确的邮箱格式'})

        # test5, post, invalid name
        response5 = self.client.post(reverse('auth:register'),
                                     data=test_data_generator(email='name@qq.com',
                                                              password='9a14efb4e17114337440905576c363efeb031af3',
                                                              name='  '),
                                     content_type='application/json')
        self.assertEqual(response5.status_code, 200)
        self.assertEqual(json.loads(response5.content.decode('utf-8')), {'error': '请输入正确的姓名'})

        # test6, post, invalid password
        response6 = self.client.post(reverse('auth:register'),
                                     data=test_data_generator(email='name@qq.com',
                                                              password='9a14efb4e171143374409055',
                                                              name='西西'),
                                     content_type='application/json')
        self.assertEqual(response6.status_code, 200)
        self.assertEqual(json.loads(response6.content.decode('utf-8')), {'error': '密码加密错误，请刷新重试'})

        # test7, post, valid data
        response7 = self.client.post(reverse('auth:register'),
                                     data=test_data_generator(email=test_email(1),
                                                              password='9a14efb4e17114337440905576c363efeb031af3',
                                                              name='西西'),
                                     content_type='application/json')
        self.assertEqual(response7.status_code, 200)
        self.assertEqual(json.loads(response7.content.decode('utf-8'))[0]['fields']['password'], '**************')

        # test8, post, repeated email
        response8 = self.client.post(reverse('auth:register'),
                                     data=test_data_generator(email=test_email(1),
                                                              password='9a14efb4e17114337440905576c363efeb031af3',
                                                              name='西西'),
                                     content_type='application/json')
        self.assertEqual(response8.status_code, 200)
        self.assertEqual(json.loads(response8.content.decode('utf-8')), {'error': '该邮箱已被注册'})

