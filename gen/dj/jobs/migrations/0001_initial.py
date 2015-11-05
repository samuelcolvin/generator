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
                ('key', models.CharField(primary_key=True, max_length=40, default=dj.jobs.models.generate_key, unique=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('timestamp_created', models.DateTimeField(auto_created=True)),
                ('id', models.UUIDField(primary_key=True, db_index=True, editable=False, serialize=False, default=uuid.uuid4)),
                ('timestamp_started', models.DateTimeField(null=True, blank=True)),
                ('timestamp_complete', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(max_length=20, default='pending', choices=[('pending', 'pending'), ('in_progress', 'in_progress'), ('complete', 'complete')])),
                ('html', models.TextField(null=True, blank=True)),
                ('file_size', models.PositiveIntegerField(null=True, blank=True)),
                ('work_log', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.SlugField(max_length=63, unique=True, editable=False)),
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
