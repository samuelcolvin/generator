import uuid

import jsonfield
from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import JobStatus
from dj.resources.models import Env


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    env = models.ForeignKey(Env, verbose_name=_('Environment'))
    timestamp_created = models.DateTimeField(_('Created'), blank=True)
    timestamp_started = models.DateTimeField(_('Started'), null=True, blank=True)
    timestamp_complete = models.DateTimeField(_('Complete'), null=True, blank=True)
    status = models.CharField(_('Status'), choices=JobStatus.STATUS_CHOICES, max_length=20,
                              default=JobStatus.STATUS_PENDING)
    html = models.TextField(null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    request_data = jsonfield.JSONField(_('Request Data'), null=True, blank=True)
    work_log = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{}: {}'.format(self.org, self.id)

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
