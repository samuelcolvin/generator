# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import dj.orgs.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('email', models.EmailField(verbose_name='Email Address', unique=True, max_length=255, blank=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('member_type', models.CharField(verbose_name='Type', max_length=6, choices=[('owner', 'Owner'), ('dev', 'Developer'), ('view', 'Viewer')])),
                ('is_staff', models.BooleanField(default=False, verbose_name='Staff')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('key', models.CharField(serialize=False, unique=True, max_length=40, default=dj.orgs.models.generate_key, primary_key=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('code', models.SlugField(unique=True, editable=False, max_length=63)),
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
        migrations.AddField(
            model_name='user',
            name='org',
            field=models.ForeignKey(to='orgs.Organisation', related_name='members', null=True, blank=True),
        ),
    ]
