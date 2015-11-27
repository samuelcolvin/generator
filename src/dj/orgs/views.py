from django_crud.controllers import RichController

from .models import Organisation


class OrganisationController(RichController):
    model = Organisation
