import uuid
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=255)


class Job(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_HTML_GENERATED = 'html_generated'
    STATUS_COMPLETE = 'complete'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_HTML_GENERATED, 'html_generated'),
        (STATUS_COMPLETE, 'complete'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organisation)
    timestamp_created = models.DateTimeField(auto_created=True)
    timestamp_complete = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=STATUS_PENDING)
    html = models.TextField(null=True, blank=True)
    file_link = models.URLField()
    work_log = models.TextField(null=True, blank=True)
