# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-15 09:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='is_ncg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='member',
            name='is_ncg_officer',
            field=models.BooleanField(default=False),
        ),
    ]