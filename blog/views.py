from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render
import json
# Create your views here.
from .utilities import Page, get_page_index
from .models import Blogs


def index(request):
    if request.method == 'GET':
        try:
            page_index = request.GET['page']
        except MultiValueDictKeyError:
            page_index = 1
        page_index = get_page_index(page_index)
        num = Blogs.objects.all().count()
        page = Page(num, page_index, 8)
        page_json = json.dumps(page, ensure_ascii=False, default=lambda obj: obj.__dict__)
        if num == 0:
            return render(request, 'index.html', {'page': page_json, 'blogs': (), 'user': request.__user__})
        blogs = Blogs.objects.order_by('-created_at')[page.offset: page.ceiling]
        return render(request, 'blog/index.html', {'page': page_json, 'blogs': blogs, 'user': request.__user__})


def blog(request):
    pass
