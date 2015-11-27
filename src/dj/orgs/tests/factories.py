import factory
from factory.django import DjangoModelFactory

from dj.orgs.models import Organisation, APIKey, User


class OrganisationFactory(DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Sequence(lambda n: 'organisation %d' % n)


class APIKeyFactory(DjangoModelFactory):
    class Meta:
        model = APIKey

    org = factory.SubFactory(OrganisationFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    password = 'testing'
    org = factory.SubFactory(OrganisationFactory)
    name = factory.Sequence(lambda n: 'user %d' % n)
    member_type = User.TYPE_OWNER
    email = factory.LazyAttribute(lambda u: '{}@example.com'.format(u.name.lower().replace(' ', '_')))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
