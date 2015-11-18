# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.UUIDField(db_index=True, editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('timestamp_created', models.DateTimeField(blank=True, verbose_name='Created')),
                ('timestamp_started', models.DateTimeField(null=True, blank=True, verbose_name='Started')),
                ('timestamp_complete', models.DateTimeField(null=True, blank=True, verbose_name='Complete')),
                ('status', models.CharField(max_length=20, default='pending', verbose_name='Status', choices=[('pending', 'pending'), ('in_progress', 'in progress'), ('complete', 'complete')])),
                ('html', models.TextField(null=True, blank=True)),
                ('file_size', models.PositiveIntegerField(null=True, blank=True)),
                ('request_data', jsonfield.fields.JSONField(null=True, blank=True, verbose_name='Request Data')),
                ('work_log', models.TextField(null=True, blank=True)),
                ('env', models.ForeignKey(verbose_name='Environment', to='resources.Env')),
            ],
            options={
                'verbose_name_plural': 'Jobs',
                'verbose_name': 'Job',
            },
        ),
    ]
