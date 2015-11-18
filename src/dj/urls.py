from django.conf.urls import include, url
from django.contrib import admin

from .jobs.views import JobController
from .organisations.views import OrganisationController

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^orgs/', include(OrganisationController.as_views('org'))),
    url(r'^jobs/', include(JobController.as_views('job'))),
]
