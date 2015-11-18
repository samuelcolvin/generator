# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dj.orgs.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('key', models.CharField(unique=True, default=dj.orgs.models.generate_key, primary_key=True, serialize=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('code', models.SlugField(editable=False, unique=True, max_length=63)),
            ],
            options={
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
            },
        ),
        migrations.AddField(
            model_name='apikey',
            name='org',
            field=models.ForeignKey(to='orgs.Organisation', related_name='api_keys'),
        ),
    ]
