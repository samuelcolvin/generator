# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='resources.File', auto_created=True)),
                ('resource_type', models.CharField(verbose_name='Type', choices=[('css', 'CSS File'), ('js', 'JS File'), ('image', 'Image File')], max_length=10)),
            ],
            bases=('resources.file',),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='resources.File', auto_created=True)),
                ('template_type', models.CharField(verbose_name='Type', choices=[('main', 'Main'), ('base', 'Base'), ('header', 'Header'), ('footer', 'Footer')], max_length=10)),
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
    ]
