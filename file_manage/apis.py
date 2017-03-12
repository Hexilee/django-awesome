from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django_awesome.settings import MEDIA_DIR
from django.core.urlresolvers import reverse
from .models import File
from .utilities import file_generator
import json
import sys
import os
from .utilities import id_generator, uuid_generator

sys.path.append('../')
auth = __import__('my_auth', globals(), locals())


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


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        if request.__user__.admin:
            admin_email = request.__user__.email
            file = request.FILES.get('file', None)
            if file:
                file_id = id_generator(uuid_generator())
                name = file.name
                size = file.size
                path = os.path.join(MEDIA_DIR, '%s_%s' % (file_id, name))

                with open(path, 'wb') as target_file:
                    for chunk in file.chunks(1024):
                        target_file.write(chunk)

                new_file = File(id=file_id, name=name, size=size, path=path, admin_email=admin_email)
                new_file.save()

                next_ = request.POST.get('next', reverse('blog:index'))
                return HttpResponseRedirect(next_)
