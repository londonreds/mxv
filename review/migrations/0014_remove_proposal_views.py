# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-23 16:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0013_proposalurl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='views',
        ),
    ]
