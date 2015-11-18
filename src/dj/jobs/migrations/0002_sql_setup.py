# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from common import JobStatus


class Migration(migrations.Migration):
    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("alter table jobs_job alter column status set default '%s';" % JobStatus.STATUS_PENDING),
        migrations.RunSQL('alter table jobs_job alter column timestamp_created set default current_timestamp;'),
    ]
