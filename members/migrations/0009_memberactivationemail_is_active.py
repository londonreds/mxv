# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-12 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_memberactivationemail_send_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberactivationemail',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
