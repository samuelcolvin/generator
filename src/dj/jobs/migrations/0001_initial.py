# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, default=uuid.uuid4, db_index=True)),
                ('timestamp_created', models.DateTimeField(blank=True, verbose_name='Created')),
                ('timestamp_started', models.DateTimeField(blank=True, verbose_name='Started', null=True)),
                ('timestamp_complete', models.DateTimeField(blank=True, verbose_name='Complete', null=True)),
                ('status', models.CharField(default='pending', verbose_name='Status', max_length=20,
                                            choices=[('pending', 'pending'),
                                                     ('in_progress', 'in progress'),
                                                     ('complete', 'complete')])),
                ('html', models.TextField(blank=True, null=True)),
                ('file_size', models.PositiveIntegerField(blank=True, null=True)),
                ('work_log', models.TextField(blank=True, null=True)),
                ('template', models.ForeignKey(verbose_name='Template', to='resources.Template')),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Jobs',
            },
        ),
    ]
