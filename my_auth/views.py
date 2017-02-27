from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.urlresolvers import reverse

import datetime
import json

# Create your views here.
from django_awesome.settings import EXPIRED_TIME, TOKEN_NAME
from .utilites import token_generator, image_generator, _RE_EMAIL, _RE_SHA1, password_generator
from .models import Users, Tokens


@csrf_exempt
def login(request):
    if request.method == 'GET':
        redirect_next = request.GET.get('next', '/blog/')
        return render(request, 'my_auth/login.html', dict(next=redirect_next))
    if request.method == 'POST':
        try:
            dict_data = json.loads(request.body.decode('utf-8'), )
        except Exception:
            return HttpResponse(json.dumps({'error': '没有数据输入！'}, ensure_ascii=False))
        email = dict_data.get('email')
        password = dict_data.get('password')

        if not email or not _RE_EMAIL.match(email):
            return HttpResponse(json.dumps({'error': '请输入正确的邮箱格式'}, ensure_ascii=False))
        if not password or not _RE_SHA1.match(password):
            raise HttpResponse(json.dumps({'error': '密码加密错误，请刷新重试'}, ensure_ascii=False))

        sha1_password = password_generator(password)
        users = Users.objects.filter(email=email)
        if not len(users) == 1:
            return HttpResponse(json.dumps({'error': '账号邮箱不存在'}, ensure_ascii=False))

        user = users[0]
        if not user.password == sha1_password:
            return HttpResponse(json.dumps({'error': '密码错误'}, ensure_ascii=False))

        token_value = token_generator(sha1_password)
        new_token = Tokens(created_at=timezone.now(),
                           expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                           user_email=email,
                           value=token_value)
        new_token.save()

        user.current_token = new_token
        user.save()

        user.password = '***************'
        r = HttpResponse(serializers.serialize('json', (user,)))
        r.set_cookie(TOKEN_NAME, token_value, max_age=3600 * EXPIRED_TIME, httponly=True)
        return r


@csrf_exempt
def register(request):
    if request.method == 'GET':
        redirect_next = request.GET.get('next', '/blog/')
        return render(request, 'my_auth/register.html', dict(next=redirect_next))
    if request.method == 'POST':
        try:
            dict_data = json.loads(request.body.decode('utf-8'), )
        except Exception:
            raise ValueError('No data posted ')

        email = dict_data.get('email')
        name = dict_data.get('name')
        password = dict_data.get('password')

        if not email or not _RE_EMAIL.match(email):
            return HttpResponse(json.dumps({'error': '请输入正确的邮箱格式'}, ensure_ascii=False))
        if not name or not name.strip():
            return HttpResponse(json.dumps({'error': '请输入正确的姓名'}, ensure_ascii=False))
        if not password or not _RE_SHA1.match(password):
            raise ValueError('password')
        users = Users.objects.filter(email=email)
        if len(users) > 0:
            return HttpResponse(json.dumps({'error': '该邮箱已被注册'}, ensure_ascii=False))

        # password enciphered twice
        sha1_password = password_generator(password)

        # get token
        token_value = token_generator(sha1_password)
        new_token = Tokens(created_at=timezone.now(),
                           expired_at=timezone.now() + datetime.timedelta(hours=EXPIRED_TIME),
                           user_email=email,
                           value=token_value)
        new_token.save()

        # create user
        new_user = Users(name=name.strip(), email=email, password=sha1_password, created_at=timezone.now(),
                         image=image_generator(email), current_token=new_token)
        new_user.save()

        new_user.password = '**************'
        r = HttpResponse(serializers.serialize('json', (new_user,)))
        r.set_cookie(TOKEN_NAME, token_value, max_age=3600 * EXPIRED_TIME, httponly=True)
        return r


def logout(request):
    if request.method == 'GET':
        # get path before logout
        next_path = request.GET.get('next', reverse('blog:index'))

        response = HttpResponseRedirect(reverse('auth:login') + '?next=%s' % next_path)
        token_value = request.COOKIES.get(TOKEN_NAME)
        if token_value:
            response.delete_cookie(TOKEN_NAME)
        return response
