import os
import re
import jsonfield
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dj.orgs.models import Organisation


def get_upload_path(instance, filename):
    base_filename = os.path.basename(filename)
    file_path = os.path.join(instance.org.code, instance.DIRECTORY, base_filename)
    i = 0
    find_no = r'\d*\.([^\.]*)$'
    while os.path.exists(os.path.join(settings.MEDIA_ROOT, file_path)):
        i += 1
        if re.search(find_no, file_path):
            file_path = re.sub(find_no, r'{}.\1'.format(i), file_path)
        else:
            file_path = re.sub('\d*$', str(i), file_path)
    return file_path


class File(models.Model):
    DIRECTORY = 'files'
    org = models.ForeignKey(Organisation)
    ref = models.CharField(_('Ref'), max_length=255)
    file = models.FileField(_('File'), upload_to=get_upload_path, max_length=255)

    def __str__(self):
        return self.ref

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        unique_together = (
            ('org', 'ref'),
        )


class Template(File):
    DIRECTORY = 'templates'

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
    ENGINE_MUSTACHE = 'mustache'
    ENGINE_JINJA = 'jinja'
    ENGINE_CHOICES = (
        (ENGINE_MUSTACHE, _('Mustache')),
        (ENGINE_JINJA, _('Jinja2')),
    )
    template_type = models.CharField(_('Type'), max_length=10, choices=TYPE_CHOICES)
    engine = models.CharField(_('Engine'), max_length=10, choices=ENGINE_CHOICES)

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')


class Resource(File):
    DIRECTORY = 'resources'
    TYPE_CSS = 'css'
    TYPE_JS = 'js'
    TYPE_IMAGE = 'image'
    TYPE_CHOICES = (
        (TYPE_CSS, _('CSS File')),
        (TYPE_JS, _('JS File')),
        (TYPE_IMAGE, _('Image File')),
    )
    resource_type = models.CharField(_('Type'), max_length=10, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')


class Env(models.Model):
    org = models.ForeignKey(Organisation)
    name = models.SlugField(_('Name'), max_length=255)

    main_template = models.ForeignKey(Template, related_name='main_envs',
                                      limit_choices_to={'template_type': Template.TYPE_MAIN})
    base_template = models.ForeignKey(Template, related_name='base_envs', null=True, blank=True,
                                      limit_choices_to={'template_type': Template.TYPE_BASE})
    header_template = models.ForeignKey(Template, related_name='header_envs', null=True, blank=True,
                                        limit_choices_to={'template_type': Template.TYPE_HEADER})
    footer_template = models.ForeignKey(Template, related_name='footer_envs', null=True, blank=True,
                                        limit_choices_to={'template_type': Template.TYPE_FOOTER})

    resources = models.ManyToManyField(Resource, blank=True)
    template_engine = models.CharField(_('Template Engine'), max_length=10, choices=Template.ENGINE_CHOICES)
    setup = jsonfield.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Environment')
        verbose_name_plural = _('Environments')
        unique_together = (
            ('org', 'name'),
        )
