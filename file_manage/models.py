from django.db import models
from .utilities import id_generator, uuid_generator


# Create your models here.

class File(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=id_generator(uuid_generator()))
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=100)
    upload_at = models.DateTimeField(verbose_name='Uploaded at', auto_now_add=True)
    size = models.IntegerField()
    times = models.IntegerField(verbose_name='downloaded times', default=0)
    stars = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    __repr__ = __str__
