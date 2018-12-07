# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-21 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0009_auto_20170921_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apply',
            name='add_score',
        ),
        migrations.RemoveField(
            model_name='apply',
            name='score',
        ),
        migrations.AddField(
            model_name='apply',
            name='apply_score',
            field=models.FloatField(null=True, verbose_name='加分填写数值'),
        ),
    ]
