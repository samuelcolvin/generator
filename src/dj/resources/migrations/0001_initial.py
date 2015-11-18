# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


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
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('public', models.BooleanField(verbose_name='Public', default=False)),
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
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('file_ptr', models.OneToOneField(to='resources.File', auto_created=True, primary_key=True, serialize=False, parent_link=True)),
                ('template_type', models.CharField(max_length=10, choices=[('main', 'Main'), ('base', 'Base'), ('header', 'Header'), ('footer', 'Footer')], verbose_name='Type')),
            ],
            bases=('resources.file',),
        ),
        migrations.AddField(
            model_name='file',
            name='org',
            field=models.ForeignKey(to='orgs.Organisation'),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('org', 'name')]),
        ),
        migrations.AddField(
            model_name='env',
            name='base_templates',
            field=models.ManyToManyField(to='resources.Template', related_name='base_envs', blank=True),
        ),
        migrations.AddField(
            model_name='env',
            name='main_template',
            field=models.ForeignKey(to='resources.Template', related_name='main_env'),
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
