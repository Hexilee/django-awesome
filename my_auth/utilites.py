from django.utils import timezone
from django_awesome.settings import SECRET_KEY
import hashlib


def token_generator(password):
    raw = '%s:%s:%s' % (password, str(timezone.now()), SECRET_KEY)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()
