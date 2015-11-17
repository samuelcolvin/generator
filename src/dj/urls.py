from django.conf.urls import include, url
from django.contrib import admin
from .jobs import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^orgs/', include(views.OrganisationController.as_views('org'))),
    url(r'^jobs/', include(views.JobController.as_views('job'))),
]
