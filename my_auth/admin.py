from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Tokens)
admin.site.register(models.Users)
