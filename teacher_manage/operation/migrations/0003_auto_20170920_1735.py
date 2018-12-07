# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-20 09:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0002_bonuscategory_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='apply',
            name='apply_id',
            field=models.IntegerField(null=True, verbose_name='申请的id'),
        ),
        migrations.AddField(
            model_name='apply',
            name='object_id',
            field=models.CharField(max_length=10, null=True, verbose_name='申请类别id'),
        ),
        migrations.AddField(
            model_name='apply',
            name='view_state',
            field=models.TextField(null=True, verbose_name='验证参数'),
        ),
        migrations.AddField(
            model_name='apply',
            name='view_state_gen',
            field=models.CharField(max_length=50, null=True, verbose_name='验证参数生成值'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='bonus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operation.BonusDetail', verbose_name='加分类别'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='is_upload',
            field=models.BooleanField(default=False, verbose_name='是否同步到网站'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='stu_id',
            field=models.IntegerField(null=True, verbose_name='学号'),
        ),
    ]
