from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import File
from .utilities import file_generator
import json


# Create your views here.
@csrf_exempt
def get_file(request, file_id):
    files = File.objects.filter(id=file_id).exclude(is_delete=True)
    if len(files) != 1:
        return HttpResponse(json.dumps({'error': '文件不存在！'}, ensure_ascii=False))
    file = files[0]
    response = StreamingHttpResponse(file_generator(file.path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % file.name
    response['Content-Length'] = file.size
    file.times += 1
    file.save()
    return response


