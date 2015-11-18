from django.db import models
from django.utils.translation import ugettext_lazy as _

from dj.orgs.models import Organisation


class File(models.Model):
    org = models.ForeignKey(Organisation)
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        unique_together = (
            ('org', 'name'),
        )


class Template(File):
    TYPE_MAIN = 'main'
    TYPE_BASE = 'base'
    TYPE_HEADER = 'header'
    TYPE_FOOTER = 'footer'

    TYPE_CHOICES = (
        (TYPE_MAIN, _('Main')),
        (TYPE_BASE, _('Base')),
        (TYPE_HEADER, _('Header')),
        (TYPE_FOOTER, _('Footer')),
    )
    template_type = models.CharField(_('Type'), max_length=10, choices=TYPE_CHOICES)


class Resource(File):
    TYPE_CSS = 'css'
    TYPE_JS = 'js'
    TYPE_IMAGE = 'image'
    TYPE_CHOICES = (
        (TYPE_CSS, _('CSS File')),
        (TYPE_JS, _('JS File')),
        (TYPE_IMAGE, _('Image File')),
    )
    resource_type = models.CharField(_('Type'), max_length=10, choices=TYPE_CHOICES)
