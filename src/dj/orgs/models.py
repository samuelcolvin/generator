import random
import string

from transliterate import translit

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Organisation(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    code = models.SlugField(max_length=63, unique=True, editable=False)
    # TODO subaccounts eg. for companies using SAAS services.

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


class UserManager(BaseUserManager):
    def _create_user(self, user, password):
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, org, email, password=None, **kwargs):
        user = self.model(org=org, email=self.normalize_email(email), **kwargs)
        return self._create_user(user, password)

    def create_superuser(self, email, password=None, **kwargs):
        user = self.model(email=self.normalize_email(email), is_staff=True, **kwargs)
        return self._create_user(user, password)


class User(AbstractBaseUser):
    TYPE_OWNER = 'owner'
    TYPE_DEV = 'dev'
    TYPE_VIEW = 'view'
    TYPE_CHOICES = (
        (TYPE_OWNER, _('Owner')),
        (TYPE_DEV, _('Developer')),
        (TYPE_VIEW, _('Viewer')),
    )
    email = models.EmailField(verbose_name=_('Email Address'), max_length=255, blank=True, unique=True)
    name = models.CharField(_('Name'), max_length=255)
    org = models.ForeignKey(Organisation, related_name='members', null=True, blank=True)
    member_type = models.CharField(_('Type'), max_length=6, choices=TYPE_CHOICES)
    is_staff = models.BooleanField(_('Staff'), default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return '{}, {}'.format(self.name, self.email)


def generate_key():
    sys_random = random.SystemRandom()
    s = string.ascii_letters + string.digits
    return ''.join(sys_random.choice(s) for _ in range(40))


class APIKey(models.Model):
    org = models.ForeignKey(Organisation, related_name='api_keys')
    key = models.CharField(max_length=40, primary_key=True, unique=True, default=generate_key)
    creator = models.ForeignKey(User, null=True)
    # TODO test keys,
    # TODO key permissions, eg. readonly, resources, create_jobs

    def __str__(self):
        return '{}: "{}"'.format(self.org, self.key)
