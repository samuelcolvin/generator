import uuid
import random
import string
from django.db import models
from common import JobStatus


class Organisation(models.Model):
    name = models.CharField(max_length=255)
    code = models.SlugField(max_length=63, unique=True)

    def __str__(self):
        return self.name


def generate_key():
    sys_random = random.SystemRandom()
    s = string.ascii_letters + string.digits
    return ''.join(sys_random.choice(s) for _ in range(40))


class APIKey(models.Model):
    org = models.ForeignKey(Organisation, related_name='api_keys')
    key = models.CharField(max_length=40, primary_key=True, unique=True, default=generate_key)

    def __str__(self):
        return '{}: "{}"'.format(self.org, self.key)


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    org = models.ForeignKey(Organisation)
    timestamp_created = models.DateTimeField(auto_created=True)
    timestamp_started = models.DateTimeField(null=True, blank=True)
    timestamp_complete = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=JobStatus.STATUS_CHOICES, max_length=20, default=JobStatus.STATUS_PENDING)
    html = models.TextField(null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    work_log = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{}: {}'.format(self.org, self.id)
