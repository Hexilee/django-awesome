from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers
from .models import Blogs, Comments
import json


def api_blog_list(request):
    pass


@csrf_exempt
def api_blog_comments(request, blog_id):
    if request.method == 'POST':
        try:
            data_dict = json.loads(request.body.decode('utf-8'), )
        except Exception:
            return HttpResponse(json.dumps({'error': '数据格式错误！'}, ensure_ascii=False))

        content = data_dict.get('content')
        if not content or not content.strip():
            return HttpResponse(json.dumps({'error': '请输入评论'}, ensure_ascii=False))
        content = content.strip()
        user = request.__user__
        blogs = Blogs.objects.filter(pk=blog_id)
        if not len(blogs) == 1:
            return HttpResponse(json.dumps({'error': '日志不存在！'}, ensure_ascii=False))
        blog = blogs[0]
        new_comment = Comments(user=user, blog=blog, content=content)
        new_comment.save()
        return HttpResponse(serializers.serialize('json', (new_comment, )))


def api_comments_delete(request, comment_id):
    pass
