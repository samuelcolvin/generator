import factory
from factory.django import DjangoModelFactory, FileField

from dj.resources.models import Template, Resource, Env


class TemplateFactory(DjangoModelFactory):
    class Meta:
        model = Template

    ref = factory.Sequence(lambda n: 'template_ref_%d' % n)
    org = factory.SubFactory('dj.orgs.models.OrganisationFactory')
    file = FileField(filename='template.html', data=b'Name: {{ name }}')
    template_type = Template.TYPE_MAIN
    engine = Template.ENGINE_MUSTACHE


class ResourceFactory(DjangoModelFactory):
    class Meta:
        model = Resource

    ref = factory.Sequence(lambda n: 'resource_ref_%d' % n)
    org = factory.SubFactory('dj.orgs.models.OrganisationFactory')
    file = FileField(filename='main.js', data=b'var v = "hello";')
    resource_type = Resource.TYPE_JS


class EnvFactory(DjangoModelFactory):
    class Meta:
        model = Env

    org = factory.SubFactory('dj.orgs.models.OrganisationFactory')
    name = factory.Sequence(lambda n: 'name %d' % n)
    main_template = factory.SubFactory(TemplateFactory)
    template_engine = Template.ENGINE_MUSTACHE

    @factory.post_generation
    def resources(self, create, resources, **kwargs):
        for r in resources:
            self.resources.add(r)
