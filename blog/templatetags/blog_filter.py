from django import template
from django.utils import timezone
from datetime import datetime

import time

register = template.Library()


@register.filter
def datetime_filter(date_time):  # date_time is a datetime.datetime object, => timezone.now()
    my_time = int(time.time() - date_time.timestamp())
    if my_time < 60:
        return u'1分钟前'
    if my_time < 3600:
        return u'%s分钟前' % (my_time // 60)
    if my_time < 86400:
        return u'%s小时前' % (my_time // 3600)
    if my_time < 604800:
        return u'%s天前' % (my_time // 86400)
    dt = date_time
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)
