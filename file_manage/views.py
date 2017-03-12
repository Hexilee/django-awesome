from django.shortcuts import render

# Create your views here.
from .models import File


def file_upload(request):
    if request.method == 'GET':
        redirect_next = request.GET.get('next', '/blog/')
        return render(request, 'file_name/file_upload.html', dict(next=redirect_next))
