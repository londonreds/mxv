# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-26 16:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('review', '0023_remove_track_urgent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('text', models.TextField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='TrackVoting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.CharField(max_length=100)),
                ('voting_start', models.DateField(blank=True, default=None, null=True)),
                ('voting_end', models.DateField(blank=True, default=None, null=True)),
                ('track', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='voting', to='review.Track')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL)),
                ('track_voting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='review.TrackVoting')),
            ],
        ),
        migrations.RemoveField(
            model_name='amendmenthistory',
            name='amendment',
        ),
        migrations.RemoveField(
            model_name='proposalhistory',
            name='proposal',
        ),
        migrations.RemoveField(
            model_name='proposalurl',
            name='external',
        ),
        migrations.DeleteModel(
            name='AmendmentHistory',
        ),
        migrations.DeleteModel(
            name='ProposalHistory',
        ),
        migrations.AddField(
            model_name='question',
            name='track_voting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='review.TrackVoting'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='review.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='choice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='review.Choice'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='review.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='vote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='review.Vote'),
        ),
    ]
