# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-25 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0017_moderationrequestnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderationrequest',
            name='moderated',
            field=models.BooleanField(default=False),
        ),
    ]
