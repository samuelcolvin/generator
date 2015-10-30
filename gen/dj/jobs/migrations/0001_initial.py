# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dj.jobs.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('key', models.CharField(default=dj.jobs.models.generate_key, serialize=False, max_length=40, primary_key=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('timestamp_created', models.DateTimeField(auto_created=True)),
                ('id', models.UUIDField(default=uuid.uuid4, db_index=True, primary_key=True, serialize=False, editable=False)),
                ('timestamp_complete', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='pending', choices=[('pending', 'pending'), ('in_progress', 'in_progress'), ('html_generated', 'html_generated'), ('complete', 'complete')], max_length=20)),
                ('html', models.TextField(blank=True, null=True)),
                ('file_link', models.URLField(null=True, blank=True)),
                ('work_log', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='org',
            field=models.ForeignKey(to='jobs.Organisation'),
        ),
        migrations.AddField(
            model_name='apikey',
            name='org',
            field=models.ForeignKey(related_name='api_keys', to='jobs.Organisation'),
        ),
    ]
