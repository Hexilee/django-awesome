from django.utils import timezone
from django_awesome.settings import SECRET_KEY
import hashlib
import re

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


def token_generator(password):
    raw = '%s:%s:%s' % (password, str(timezone.now()), SECRET_KEY)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()


def image_generator(email):
    return 'https://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest()