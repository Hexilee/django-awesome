from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render
from django.shortcuts import get_object_or_404
import json
# Create your views here.
from .utilities import Page, get_page_index, text_to_html
from .models import Blogs, Comments
from . import markdown2


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
            return render(request, 'index.html',
                          {'page': page_json, 'blogs': (), 'user': request.__user__})
        blogs = Blogs.objects.order_by('-created_at')[page.offset: page.ceiling]
        return render(request, 'blog/index.html',
                      {'page': page_json, 'blogs': blogs, 'user': request.__user__})


def get_blog(request, blog_id):
    if request.method == 'GET':
        blog = get_object_or_404(Blogs, pk=blog_id)
        blog.html_content = markdown2.markdown(blog.content)
        comments = Comments.objects.filter(blog_id=blog_id)
        if len(comments) == 0:
            comments = None
        else:
            for c in comments:
                c.html_content = text_to_html(c.content)
        context = dict(blog=blog, comments=comments, user=request.__user__)
        return render(request, 'blog/blog.html', context=context)
