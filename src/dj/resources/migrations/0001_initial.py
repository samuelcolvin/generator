# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import dj.resources.models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Env',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.SlugField(max_length=255, verbose_name='Name')),
                ('setup', jsonfield.fields.JSONField(null=True, blank=True)),
                ('org', models.ForeignKey(to='orgs.Organisation')),
                ('template_engine', models.CharField(verbose_name='Template Engine', choices=[('mustache', 'Mustache'), ('jinja', 'Jinja2')], max_length=10)),
            ],
            options={
                'verbose_name_plural': 'Environments',
                'verbose_name': 'Environment',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('ref', models.CharField(max_length=255, verbose_name='Ref')),
                ('file', models.FileField(max_length=255, upload_to=dj.resources.models.get_upload_path, verbose_name='File')),
            ],
            options={
                'verbose_name_plural': 'Files',
                'verbose_name': 'File',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('file_ptr', models.OneToOneField(to='resources.File', auto_created=True, primary_key=True, serialize=False, parent_link=True)),
                ('resource_type', models.CharField(max_length=10, choices=[('css', 'CSS File'), ('js', 'JS File'), ('image', 'Image File')], verbose_name='Type')),
            ],
            bases=('resources.file',),
            options={
                'verbose_name_plural': 'Resources',
                'verbose_name': 'Resource',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('file_ptr', models.OneToOneField(to='resources.File', auto_created=True, primary_key=True, serialize=False, parent_link=True)),
                ('template_type', models.CharField(max_length=10, choices=[('main', 'Main'), ('base', 'Base'), ('header', 'Header'), ('footer', 'Footer')], verbose_name='Type')),
                ('engine', models.CharField(verbose_name='Engine', choices=[('mustache', 'Mustache'), ('jinja', 'Jinja2')], max_length=10)),
            ],
            bases=('resources.file',),
            options={
                'verbose_name_plural': 'Templates',
                'verbose_name': 'Template',
            },
        ),
        migrations.AddField(
            model_name='file',
            name='org',
            field=models.ForeignKey(to='orgs.Organisation'),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('org', 'ref')]),
        ),
        migrations.AddField(
            model_name='env',
            name='main_template',
            field=models.ForeignKey(to='resources.Template', related_name='main_envs'),
        ),
        migrations.AddField(
            model_name='env',
            name='base_template',
            field=models.ForeignKey(related_name='base_envs', null=True, blank=True, to='resources.Template'),
        ),
        migrations.AddField(
            model_name='env',
            name='footer_template',
            field=models.ForeignKey(related_name='footer_envs', null=True, blank=True, to='resources.Template'),
        ),
        migrations.AddField(
            model_name='env',
            name='header_template',
            field=models.ForeignKey(related_name='header_envs', null=True, blank=True, to='resources.Template'),
        ),
        migrations.AddField(
            model_name='env',
            name='resources',
            field=models.ManyToManyField(to='resources.Resource', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='env',
            unique_together=set([('org', 'name')]),
        ),
    ]
