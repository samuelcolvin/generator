import random
import string

from transliterate import translit

from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Organisation(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    code = models.SlugField(max_length=63, unique=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')


def smart_slugify(name, min_length=3):
    """
    Wrapper for slugify which tries hard to come up with a slug for unicode strings and if it still fails
    generates a random slug.
    """
    url_slug = slugify(name)
    if len(url_slug) >= min_length:
        return url_slug
    # try converting to latin characters:
    for lang in ('ru', 'ka', 'hy', 'el', 'bg', 'uk'):
        trans_url_slug = slugify(translit(name, lang, reversed=True))
        if len(trans_url_slug) >= min_length:
            return trans_url_slug
    # if the url is random lets make it slightly longer
    min_length = 6
    return url_slug + ''.join([random.choice(string.ascii_lowercase) for _ in range(min_length - len(url_slug))])


@receiver(models.signals.pre_save, sender=Organisation)
def generate_code(instance, **kwargs):
    if instance.id is None:
        instance.code = smart_slugify(instance.code or instance.name)


def generate_key():
    sys_random = random.SystemRandom()
    s = string.ascii_letters + string.digits
    return ''.join(sys_random.choice(s) for _ in range(40))


class APIKey(models.Model):
    org = models.ForeignKey(Organisation, related_name='api_keys')
    key = models.CharField(max_length=40, primary_key=True, unique=True, default=generate_key)

    def __str__(self):
        return '{}: "{}"'.format(self.org, self.key)
