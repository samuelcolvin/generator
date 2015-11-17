from django_crud.controllers import RichController

from .models import Organisation, Job


class OrganisationController(RichController):
    model = Organisation


class JobController(RichController):
    model = Job
    list_display_items = [
        'link|id',
        'timestamp_created',
        'status',
    ]

    detail_display_items = [
        'id',
        'timestamp_created',
        'timestamp_started',
        'timestamp_complete',
        'status',
        'html',
        'file_size',
        'work_log',
    ]
    detail_url = r'details/(?P<pk>[^/]+)/$'

    create_view = None
    update_view = None
    delete_view = None
