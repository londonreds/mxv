# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-23 14:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0012_auto_20180122_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(max_length=1000)),
                ('display_text', models.TextField(max_length=1000)),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='review.Proposal')),
            ],
        ),
    ]
