import shutil

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import connection

from dj.orgs.tests.factories import OrganisationFactory, APIKeyFactory, UserFactory
from dj.resources.models import Template
from dj.resources.tests.factories import TemplateFactory, ResourceFactory, EnvFactory


class Command(BaseCommand):
    help = 'reset database and create fresh organisation and associated paraphernalia.'

    def handle(self, *args, **options):
        if input('Are you sure you want to DESTROY ALL DATA irreversibly? [yes/NO] ') != 'yes':
            print('cancelled')
            return
        cur = connection.cursor()
        cur.execute('DROP SCHEMA public CASCADE;')
        cur.execute('CREATE SCHEMA public;')

        call_command('migrate')
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        org = OrganisationFactory()
        print('Organisation created:', org)
        user = UserFactory(org=org)
        print('User created: email: {}, password: "testing"'.format(user.email))
        api_key = APIKeyFactory(org=org)
        print('API Key Created:', api_key.key)

        EnvFactory(
            org=org,
            main_template__org=org,
            base_template=TemplateFactory(org=org, template_type=Template.TYPE_BASE),
            header_template=TemplateFactory(org=org, template_type=Template.TYPE_HEADER),
            footer_template=TemplateFactory(org=org, template_type=Template.TYPE_FOOTER),
            resources=[
                ResourceFactory(org=org),
                ResourceFactory(org=org),
            ]
        )
