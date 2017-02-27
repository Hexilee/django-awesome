# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-27 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogs',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='blogs',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_auth.Users'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created'),
        ),
    ]
