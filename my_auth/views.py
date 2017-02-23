from django.shortcuts import render
from django.utils import timezone
from django_awesome.settings import SECRET_KEY
import hashlib
import datetime


# Create your views here.

def token_generator(password):
    raw = '%s:%s:%s' % (password, str(timezone.now()), SECRET_KEY)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()


def login(request):
    pass


def register(request):
    pass
