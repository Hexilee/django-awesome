from django.contrib import admin

# Register your models here.
from . import models


admin.site.register(models.Blogs)
admin.site.register(models.Comments)
