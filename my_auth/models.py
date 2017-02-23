from django.db import models


# Create your models here.


class Tokens(models.Model):
    cookie = models.CharField(max_length=100)
    created_at = models.DateTimeField('date created')
    expire_at = models.DateTimeField('date expired')
    user_email = models.CharField(max_length=50)

    def __str__(self):
        return self.cookie

    __repr__ = __str__


class Users(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    image = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField('date created')
    current_token = models.ForeignKey(Tokens, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    __repr__ = __str__
